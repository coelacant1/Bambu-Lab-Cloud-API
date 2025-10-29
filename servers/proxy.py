#!/usr/bin/env python3
"""
Bambu Lab Cloud API Proxy Server
===========================

A unified proxy with multiple modes for different use cases.

Modes:
  - strict: Only GET requests allowed (port 5001)
  - full: Complete 1:1 proxy with all operations (port 5003)

Usage:
  python proxy.py [mode]
  
  mode: strict or full (default: strict)
"""

import sys
import os
import re
import copy
import time
import atexit
import threading
from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add parent directory to path for bambulab import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import BambuClient, TokenManager, MQTTClient
from bambulab.client import BambuAPIError

app = Flask(__name__)

# Configuration
PROXY_MODE = "strict"  # strict or full
TOKEN_FILE = "proxy_tokens.json"

# Port mapping by mode
PORTS = {
    "strict": 5001,
    "full": 5003
}

# Rate limiting configuration (1/4 of Bambu Cloud API limits)
# Based on expected Bambu Cloud limits:
#   Device Queries: 120/min -> 30/min
#   User Profile: 60/min -> 15/min
#   Task History: 60/min -> 15/min
RATE_LIMITS = {
    "default": "30 per minute",      # General API calls
    "user": "15 per minute",         # User endpoints
    "admin": "10 per minute",        # Admin endpoints
    "health": "60 per minute"        # Health checks (more lenient)
}

# Initialize rate limiter
# Uses token from Authorization header as key for per-token limiting
def get_token_key():
    """Extract token from Authorization header for rate limiting"""
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()
    if token:
        return f"token:{token}"
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_token_key,
    default_limits=[RATE_LIMITS["default"]],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,  # Ensure rate limit headers are sent
    swallow_errors=False   # Show rate limit errors
)

# Global token manager and MQTT cache
token_manager = None
mqtt_sessions = {}  # device_id -> {'client': MQTTClient, 'data': {}, 'expires': timestamp}
mqtt_config = {
    'session_duration': 120,  # 2 minutes in seconds
    'cleanup_interval': 30     # Check for expired sessions every 30s
}


def mask_sensitive_data(data, custom_token=None):
    """
    Recursively mask sensitive data in API responses.
    
    Masks:
    - Device access codes (dev_access_code)
    - URLs (http://, https://, ftp://)
    - IP addresses
    - Tokens (any field containing 'token')
    - Custom tokens passed to proxy
    
    Args:
        data: Response data (dict, list, or primitive)
        custom_token: The custom token to mask if found
        
    Returns:
        Masked copy of data
    """
    if data is None:
        return None
    
    # Work with a deep copy to avoid modifying original
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Mask device access codes
            if key_lower in ['dev_access_code', 'access_code', 'accesscode']:
                result[key] = "********"
            # Mask any field containing 'token'
            elif 'token' in key_lower and isinstance(value, str):
                result[key] = mask_token(value)
            # Recursively process nested structures
            elif isinstance(value, (dict, list)):
                result[key] = mask_sensitive_data(value, custom_token)
            # Mask URLs and IPs in string values
            elif isinstance(value, str):
                result[key] = mask_urls_and_ips(value, custom_token)
            else:
                result[key] = value
        return result
        
    elif isinstance(data, list):
        return [mask_sensitive_data(item, custom_token) for item in data]
    
    elif isinstance(data, str):
        return mask_urls_and_ips(data, custom_token)
    
    else:
        return data


def mask_token(token):
    """Mask a token, showing only first 20 chars"""
    if not token or len(token) < 10:
        return "***"
    return token[:20] + "..."


def mask_urls_and_ips(text, custom_token=None):
    """
    Mask URLs, IP addresses, and custom tokens in text.
    
    Args:
        text: String to mask
        custom_token: Custom token to mask if found
        
    Returns:
        Masked string
    """
    if not isinstance(text, str):
        return text
    
    # Mask custom token if provided
    if custom_token and custom_token in text:
        text = text.replace(custom_token, "***REDACTED***")
    
    # Mask URLs (http://, https://, ftp://)
    text = re.sub(
        r'(https?|ftp)://[^\s<>"{}|\\^`\[\]]+',
        '[URL_REDACTED]',
        text
    )
    
    # Mask IP addresses (but preserve localhost references)
    text = re.sub(
        r'\b(?:(?!127\.0\.0\.1)(?!localhost)(?:\d{1,3}\.){3}\d{1,3})\b',
        '[IP_REDACTED]',
        text
    )
    
    return text


def mqtt_message_handler(device_id):
    """Factory function to create message handler for specific device"""
    def handler(dev_id, data):
        """Callback for MQTT messages - updates cache"""
        global mqtt_sessions
        if device_id in mqtt_sessions:
            mqtt_sessions[device_id]['data'] = data
            mqtt_sessions[device_id]['timestamp'] = time.time()
            mqtt_sessions[device_id]['message_count'] = mqtt_sessions[device_id].get('message_count', 0) + 1
    return handler


def init_token_manager():
    """Initialize the token manager."""
    global token_manager
    token_manager = TokenManager(TOKEN_FILE)
    print(f"Loaded {token_manager.count()} token mappings")


def cleanup_expired_mqtt_sessions():
    """Background thread to cleanup expired MQTT sessions"""
    global mqtt_sessions
    
    while True:
        try:
            time.sleep(mqtt_config['cleanup_interval'])
            now = time.time()
            expired = []
            
            for device_id, session in mqtt_sessions.items():
                if now > session['expires']:
                    expired.append(device_id)
            
            for device_id in expired:
                session = mqtt_sessions[device_id]
                try:
                    session['client'].disconnect()
                    print(f"[MQTT] Session expired for device {device_id}")
                except:
                    pass
                del mqtt_sessions[device_id]
                
        except Exception as e:
            print(f"[MQTT] Cleanup error: {e}")


def start_mqtt_session(device_id: str, real_token: str):
    """
    Start MQTT monitoring session for a specific device.
    
    Returns:
        dict: Session info or error
    """
    global mqtt_sessions
    
    # Check if session already exists and is valid
    if device_id in mqtt_sessions:
        session = mqtt_sessions[device_id]
        if time.time() < session['expires']:
            # Extend existing session
            session['expires'] = time.time() + mqtt_config['session_duration']
            return {
                'status': 'extended',
                'device_id': device_id,
                'expires_in': mqtt_config['session_duration'],
                'message': 'Existing session extended'
            }
        else:
            # Clean up expired session
            try:
                session['client'].disconnect()
            except:
                pass
            del mqtt_sessions[device_id]
    
    try:
        # Get user profile for username
        client = BambuClient(real_token)
        profile = client.get(f"v1/user-service/my/profile")
        username = profile.get('uid') or profile.get('user_id')
        
        if not username:
            return {'error': 'Failed to get user ID', 'status': 'failed'}
        
        # Create MQTT client
        mqtt_client = MQTTClient(
            username=str(username),
            access_token=real_token,
            device_id=device_id,
            on_message=mqtt_message_handler(device_id)
        )
        
        mqtt_client.connect(blocking=False)
        
        # Wait briefly for connection
        time.sleep(1)
        
        if not mqtt_client.connected:
            return {'error': 'MQTT connection failed', 'status': 'failed'}
        
        # Request full status
        mqtt_client.request_full_status()
        
        # Create session
        mqtt_sessions[device_id] = {
            'client': mqtt_client,
            'data': {},
            'timestamp': None,
            'expires': time.time() + mqtt_config['session_duration'],
            'started': time.time(),
            'message_count': 0
        }
        
        return {
            'status': 'started',
            'device_id': device_id,
            'expires_in': mqtt_config['session_duration'],
            'message': f'MQTT monitoring started for {mqtt_config["session_duration"]} seconds'
        }
        
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}


@app.before_request
def check_strict_mode():
    """Reject non-GET requests in strict mode (except MQTT start endpoint)."""
    # Allow POST to MQTT start endpoint even in strict mode
    if request.path == '/v1/iot-service/api/user/device/realtime/start':
        return None
    
    if PROXY_MODE == "strict" and request.method != 'GET' and request.path not in ['/health', '/']:
        return jsonify({
            "error": "Method Not Allowed",
            "message": "This proxy only supports GET requests in strict mode",
            "allowed_methods": ["GET"]
        }), 405


@app.route('/health', methods=['GET'])
@limiter.limit(RATE_LIMITS["health"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "mode": PROXY_MODE,
        "backend": BambuClient.BASE_URL,
        "tokens_configured": token_manager.count() if token_manager else 0,
        "mqtt_active_sessions": len(mqtt_sessions),
        "mqtt_session_duration": f"{mqtt_config['session_duration']} seconds",
        "rate_limits": {
            "device_queries": "30 per minute",
            "user_endpoints": "15 per minute",
            "admin_endpoints": "10 per minute"
        }
    })


@app.route('/', methods=['GET'])
@limiter.limit(RATE_LIMITS["health"])
def info():
    """API information endpoint."""
    descriptions = {
        "strict": "Only GET requests are allowed. All other methods return 405.",
        "full": "Complete 1:1 proxy. All requests forwarded to real API including write operations."
    }
    
    response_data = {
        "name": "Bambu Lab Cloud API Proxy",
        "version": "2.2.0",
        "mode": PROXY_MODE,
        "description": descriptions[PROXY_MODE],
        "endpoints": {
            "health": "/health",
            "admin_tokens": "/admin/tokens",
            "api_base": "/v1/"
        },
        "rate_limits": {
            "device_queries": "30 per minute",
            "user_endpoints": "15 per minute",
            "admin_endpoints": "10 per minute",
            "health_check": "60 per minute"
        }
    }
    
    if PROXY_MODE == "full":
        response_data["warning"] = "WARNING: This proxy allows actual modifications to your printers"
    
    return jsonify(response_data)


@app.route('/v1/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy_v1(endpoint):
    """Proxy all /v1/* requests."""
    # Extract and validate token
    custom_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not custom_token:
        return jsonify({
            "error": "Missing token",
            "message": "Authorization header required"
        }), 401
    
    real_token = token_manager.validate(custom_token)
    if not real_token:
        return jsonify({
            "error": "Invalid token",
            "message": "Unauthorized"
        }), 401
    
    # Apply rate limiting based on endpoint type
    # User endpoints get lower limit (15/min)
    if 'user-service' in endpoint or 'design-user-service' in endpoint:
        limiter.limit(RATE_LIMITS["user"])(lambda: None)()
    # Device endpoints get default limit (30/min)
    else:
        limiter.limit(RATE_LIMITS["default"])(lambda: None)()
    
    # Create client with real token
    client = BambuClient(real_token)
    
    # Get request body for write operations
    data = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            data = request.get_json(silent=True) or {}
        except:
            data = {}
    
    # Make request using BambuClient
    try:
        if request.method == 'GET':
            result = client.get(f"v1/{endpoint}", params=dict(request.args))
        elif request.method == 'POST':
            result = client.post(f"v1/{endpoint}", data=data)
        elif request.method == 'PUT':
            result = client.put(f"v1/{endpoint}", data=data)
        elif request.method == 'DELETE':
            result = client.delete(f"v1/{endpoint}")
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        # Mask sensitive data before returning
        if result is not None:
            masked_result = mask_sensitive_data(result, custom_token)
            return jsonify(masked_result)
        else:
            return '', 204  # No content
            
    except BambuAPIError as e:
        # Mask sensitive data in error messages too
        error_msg = mask_urls_and_ips(str(e), custom_token)
        return jsonify({
            "error": "API request failed",
            "message": error_msg
        }), 502


@app.route('/v1/iot-service/api/user/device/realtime/start', methods=['POST'])
@limiter.limit(RATE_LIMITS["default"])
def start_realtime_monitoring():
    """Start MQTT monitoring session for a device"""
    # Validate token
    custom_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not custom_token:
        return jsonify({"error": "Missing token"}), 401
    
    real_token = token_manager.validate(custom_token)
    if not real_token:
        return jsonify({"error": "Invalid token"}), 401
    
    # Get device_id from request body
    try:
        data = request.get_json()
        device_id = data.get('device_id')
    except:
        return jsonify({"error": "Invalid JSON"}), 400
    
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    # Start MQTT session
    result = start_mqtt_session(device_id, real_token)
    
    if result.get('status') in ['started', 'extended']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/v1/iot-service/api/user/device/realtime', methods=['GET'])
@limiter.limit(RATE_LIMITS["default"])
def get_realtime_data():
    """Get cached real-time MQTT data for a device"""
    # Validate token
    custom_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not custom_token:
        return jsonify({"error": "Missing token"}), 401
    
    real_token = token_manager.validate(custom_token)
    if not real_token:
        return jsonify({"error": "Invalid token"}), 401
    
    # Require device_id parameter
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({
            "error": "device_id required",
            "message": "Specify device_id parameter or start monitoring with POST to /v1/iot-service/api/user/device/realtime/start"
        }), 400
    
    # Check if session exists
    if device_id not in mqtt_sessions:
        return jsonify({
            "error": "No active monitoring session",
            "message": "Start monitoring by POST to /v1/iot-service/api/user/device/realtime/start with device_id",
            "device_id": device_id
        }), 404
    
    session = mqtt_sessions[device_id]
    now = time.time()
    
    # Check if session expired
    if now > session['expires']:
        return jsonify({
            "error": "Monitoring session expired",
            "message": "Session expired. Start new session by POST to /v1/iot-service/api/user/device/realtime/start",
            "device_id": device_id
        }), 410  # 410 Gone
    
    # Check if we have data yet
    if not session.get('data'):
        return jsonify({
            "status": "waiting",
            "message": "Waiting for first MQTT message",
            "device_id": device_id,
            "session_age": now - session['started'],
            "expires_in": session['expires'] - now
        }), 202  # 202 Accepted (processing)
    
    # Return data
    return jsonify({
        "device_id": device_id,
        "data": mask_sensitive_data(session['data'], custom_token),
        "timestamp": session.get('timestamp'),
        "age_seconds": now - session['timestamp'] if session.get('timestamp') else None,
        "expires_in": session['expires'] - now,
        "message_count": session.get('message_count', 0)
    })


@app.route('/admin/tokens', methods=['GET'])
@limiter.limit(RATE_LIMITS["admin"])
def list_tokens():
    """List configured tokens (without exposing real tokens)"""
    tokens_list = [
        {
            "custom_token": custom,
            "has_real_token": True
        }
        for custom, masked in token_manager.list_tokens().items()
    ]
    return jsonify({
        "tokens": tokens_list,
        "count": token_manager.count()
    })


@app.route('/admin/mqtt', methods=['GET'])
@limiter.limit(RATE_LIMITS["admin"])
def mqtt_status():
    """Get MQTT monitoring status"""
    now = time.time()
    sessions = {}
    
    for device_id, session in mqtt_sessions.items():
        sessions[device_id] = {
            "connected": session['client'].connected,
            "message_count": session.get('message_count', 0),
            "last_update": session.get('timestamp'),
            "has_data": bool(session.get('data')),
            "expires_in": session['expires'] - now,
            "session_age": now - session['started']
        }
    
    return jsonify({
        "active_sessions": len(mqtt_sessions),
        "session_duration": mqtt_config['session_duration'],
        "cleanup_interval": mqtt_config['cleanup_interval'],
        "sessions": sessions
    })


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(e.description),
        "retry_after": "60 seconds"
    }), 429


def main():
    """Main entry point."""
    global PROXY_MODE
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in PORTS:
            PROXY_MODE = mode
        else:
            print(f"Error: Invalid mode '{mode}'")
            print("Valid modes: strict, full")
            sys.exit(1)
    
    # Initialize token manager
    init_token_manager()
    
    # Start MQTT cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired_mqtt_sessions, daemon=True)
    cleanup_thread.start()
    print("MQTT session cleanup thread started")
    
    # Register cleanup handler
    def cleanup():
        """Cleanup on shutdown"""
        print("\nShutting down...")
        for device_id, session in mqtt_sessions.items():
            try:
                session['client'].disconnect()
                print(f"  Disconnected MQTT for {device_id}")
            except:
                pass
    
    atexit.register(cleanup)
    
    # Print banner
    port = PORTS[PROXY_MODE]
    print("=" * 80)
    print("Bambu Lab Cloud API Proxy Server")
    print("=" * 80)
    print(f"Mode: {PROXY_MODE}")
    print(f"Port: {port}")
    print(f"Backend: {BambuClient.BASE_URL}")
    print(f"Tokens: {token_manager.count()} configured")
    print()
    
    print("Rate Limits (per token):")
    print(f"  Device Queries: {RATE_LIMITS['default']}")
    print(f"  User Endpoints: {RATE_LIMITS['user']}")
    print(f"  Admin Endpoints: {RATE_LIMITS['admin']}")
    print(f"  Health Checks: {RATE_LIMITS['health']}")
    print()
    
    if PROXY_MODE == "strict":
        print("Behavior: Only GET requests allowed")
        print("Safety: Maximum - no writes possible")
    elif PROXY_MODE == "full":
        print("Behavior: All requests forwarded to real API")
        print("WARNING: Write operations will modify your printers!")
        print("Safety: None - use with caution")
    
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print("=" * 80)
    print()
    
    # Run server
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
