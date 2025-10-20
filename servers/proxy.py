#!/usr/bin/env python3
"""
Bambu Lab API Proxy Server
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
from flask import Flask, request, jsonify, Response

# Add parent directory to path for bambulab import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import BambuClient, TokenManager
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

# Global token manager
token_manager = None


def init_token_manager():
    """Initialize the token manager."""
    global token_manager
    token_manager = TokenManager(TOKEN_FILE)
    print(f"Loaded {token_manager.count()} token mappings")


@app.before_request
def check_strict_mode():
    """Reject non-GET requests in strict mode."""
    if PROXY_MODE == "strict" and request.method != 'GET' and request.path not in ['/health', '/']:
        return jsonify({
            "error": "Method Not Allowed",
            "message": "This proxy only supports GET requests in strict mode",
            "allowed_methods": ["GET"]
        }), 405


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "mode": PROXY_MODE,
        "backend": BambuClient.BASE_URL,
        "tokens_configured": token_manager.count() if token_manager else 0
    })


@app.route('/', methods=['GET'])
def info():
    """API information endpoint."""
    descriptions = {
        "strict": "Only GET requests are allowed. All other methods return 405.",
        "full": "Complete 1:1 proxy. All requests forwarded to real API including write operations."
    }
    
    response_data = {
        "name": "Bambu Lab API Proxy",
        "version": "2.2.0",
        "mode": PROXY_MODE,
        "description": descriptions[PROXY_MODE],
        "endpoints": {
            "health": "/health",
            "admin_tokens": "/admin/tokens",
            "api_base": "/v1/"
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
        
        # Return the result
        if result is not None:
            return jsonify(result)
        else:
            return '', 204  # No content
            
    except BambuAPIError as e:
        return jsonify({
            "error": "API request failed",
            "message": str(e)
        }), 502


@app.route('/admin/tokens', methods=['GET'])
def list_tokens():
    """List configured tokens (masked)."""
    tokens_list = [
        {
            "custom_token": custom,
            "real_token_preview": masked
        }
        for custom, masked in token_manager.list_tokens().items()
    ]
    return jsonify({
        "tokens": tokens_list,
        "count": token_manager.count()
    })


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
    
    # Print banner
    port = PORTS[PROXY_MODE]
    print("=" * 80)
    print("Bambu Lab API Proxy Server")
    print("=" * 80)
    print(f"Mode: {PROXY_MODE}")
    print(f"Port: {port}")
    print(f"Backend: {BambuClient.BASE_URL}")
    print(f"Tokens: {token_manager.count()} configured")
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
