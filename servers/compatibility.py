#!/usr/bin/env python3
"""
Bambu Lab Compatibility Layer Server
=====================================

Provides backward compatibility for legacy tools and home automation systems
that relied on the old local API access (before developer mode was removed)

Acts as a bridge between legacy clients expecting local API access and the
modern Bambu Lab Cloud API, restoring functionality without requiring developer mode.

Features:
- Mimics old local API endpoints
- Translates requests to Cloud API
- MQTT bridge for real-time updates
- Should work with Home Assistant, Octoprint, and other legacy integrations

Port 8080: HTTP API (mimics old local API)
"""

import json
import logging
import time
import sys
import os
from datetime import datetime
from typing import Dict, Optional, List, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Add parent directory to path for bambulab import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import BambuClient, MQTTBridge, Device
from bambulab.client import BambuAPIError
from bambulab.utils import format_timestamp, safe_get

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG_FILE = "compatibility_config.json"

# Global state
config = {}
api_client = None
mqtt_bridge = None
device_status_cache = {}


def load_config():
    """Load configuration from file"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logger.info(f"Loaded configuration with {len(config.get('devices', []))} devices")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file {CONFIG_FILE} not found")
        logger.info("Creating example configuration file...")
        example_config = {
            "cloud_token": "YOUR_BAMBU_CLOUD_TOKEN_HERE",
            "user_uid": "YOUR_USER_UID_HERE",
            "devices": [
                {
                    "device_id": "DEVICE_SERIAL_NUMBER",
                    "name": "My Printer",
                    "local_ip": "192.168.1.100",
                    "access_code": "12345678"
                }
            ],
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "enable_mqtt_bridge": True
            }
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(example_config, f, indent=2)
        logger.info(f"Created example configuration at {CONFIG_FILE}")
        logger.info("Please edit the configuration file with your actual credentials")
        return example_config


def init_api_client():
    """Initialize the Bambu API client"""
    global api_client
    token = config.get('cloud_token')
    if not token or token == "YOUR_BAMBU_CLOUD_TOKEN_HERE":
        logger.error("No valid cloud token configured")
        return False
    
    api_client = BambuClient(token)
    logger.info("API client initialized")
    return True


def init_mqtt_bridge():
    """Initialize the MQTT bridge for real-time updates"""
    global mqtt_bridge
    
    if not config.get('server', {}).get('enable_mqtt_bridge', True):
        logger.info("MQTT bridge disabled in configuration")
        return False
    
    username = config.get('user_uid')
    token = config.get('cloud_token')
    devices = config.get('devices', [])
    
    if not username or not token or not devices:
        logger.warning("Missing configuration for MQTT bridge")
        return False
    
    # Create callback for caching data
    def cache_device_data(device_id: str, data: Dict):
        device_status_cache[device_id] = {
            "data": data,
            "timestamp": time.time()
        }
        logger.debug(f"Cached MQTT data for {device_id}")
    
    try:
        # Initialize MQTT bridge with callback
        mqtt_bridge = MQTTBridge(
            username=username,
            access_token=token,
            devices=devices
        )
        
        # Manually set callback since MQTTBridge creates clients internally
        # We'll use the bridge's cache mechanism
        mqtt_bridge.start()
        logger.info(f"MQTT bridge started for {len(devices)} device(s)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize MQTT bridge: {e}")
        return False


def get_cached_status(device_id: str, max_age: int = 5) -> Optional[Dict]:
    """
    Get device status from cache if available and fresh.
    
    Args:
        device_id: Device serial number
        max_age: Maximum cache age in seconds
        
    Returns:
        Cached status data or None
    """
    if mqtt_bridge:
        cached = mqtt_bridge.get_cached_data(device_id)
        if cached:
            return cached
    
    # Fallback to local cache
    if device_id in device_status_cache:
        cache_entry = device_status_cache[device_id]
        if time.time() - cache_entry['timestamp'] < max_age:
            return cache_entry['data']
    
    return None


def fetch_device_status(device_id: str) -> Optional[Dict]:
    """Fetch device status from Cloud API"""
    if not api_client:
        logger.error("API client not initialized")
        return None
    
    try:
        response = api_client.get_print_status(force=True)
        devices = response.get("devices", [])
        
        for device in devices:
            if device.get("dev_id") == device_id:
                return device
        
        return None
    except BambuAPIError as e:
        logger.error(f"Error fetching device status: {e}")
        return None


def translate_to_legacy_format(cloud_data: Dict) -> Dict:
    """
    Translate Cloud API format to legacy local API format.
    Mimics the old API response structure that legacy clients expect.
    """
    if not cloud_data:
        return {}
    
    # Extract print data from nested structure if needed
    print_data = cloud_data.get('print', cloud_data)
    
    # Legacy format expected by Home Assistant, Octoprint, etc.
    legacy = {
        "print": {
            "command": "push_status",
            "msg": 0,
            "sequence_id": str(int(time.time())),
            
            # Print progress
            "mc_percent": safe_get(print_data, "mc_percent", default=0),
            "mc_remaining_time": safe_get(print_data, "mc_remaining_time", default=0),
            "print_type": safe_get(print_data, "print_type", default=""),
            "print_status": safe_get(cloud_data, "print_status", default=""),
            "gcode_state": safe_get(print_data, "gcode_state", default=""),
            "gcode_file": safe_get(print_data, "gcode_file", default=""),
            "subtask_name": safe_get(print_data, "subtask_name", default=""),
            
            # Temperature data
            "nozzle_temper": safe_get(print_data, "nozzle_temper", default=0),
            "nozzle_target_temper": safe_get(print_data, "nozzle_target_temper", default=0),
            "bed_temper": safe_get(print_data, "bed_temper", default=0),
            "bed_target_temper": safe_get(print_data, "bed_target_temper", default=0),
            "chamber_temper": safe_get(print_data, "chamber_temper", default=0),
            
            # Speed and layer info
            "spd_mag": safe_get(print_data, "spd_mag", default=100),
            "spd_lvl": safe_get(print_data, "spd_lvl", default=2),
            "layer_num": safe_get(print_data, "layer_num", default=0),
            "total_layer_num": safe_get(print_data, "total_layer_num", default=0),
            
            # AMS (Automatic Material System)
            "ams_status": safe_get(print_data, "ams_status", default=0),
            "ams_rfid_status": safe_get(print_data, "ams_rfid_status", default=0),
            
            # Lights and fans
            "lights_report": safe_get(print_data, "lights_report", default=[]),
            "fan_gear": safe_get(print_data, "fan_gear", default=0),
            
            # WiFi signal
            "wifi_signal": safe_get(cloud_data, "wifi_signal", default="-50dBm"),
            
            # Device info
            "dev_id": safe_get(cloud_data, "dev_id", default=""),
            "name": safe_get(cloud_data, "name", default=""),
            "online": safe_get(cloud_data, "online", default=False)
        }
    }
    
    return legacy


# ============================================================================
# Legacy API Endpoints (mimicking old local API)
# ============================================================================

@app.route('/')
def index():
    """Root endpoint with server information"""
    return jsonify({
        "name": "Bambu Lab Compatibility Layer",
        "version": "2.0.0",
        "description": "Restores legacy local API functionality without developer mode",
        "devices": len(config.get('devices', [])),
        "mqtt_bridge": "enabled" if mqtt_bridge else "disabled",
        "status": "online"
    })


@app.route('/api/version')
def api_version():
    """Legacy version endpoint"""
    return jsonify({
        "api_version": "1.0.0",
        "compatibility_layer": True,
        "supported_clients": [
            "Home Assistant",
            "Octoprint",
            "Repetier",
            "Custom integrations"
        ]
    })


@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """
    Legacy endpoint: Get printer status
    Mimics old local API /api/v1/status
    """
    device_id = request.args.get('device_id')
    
    if not device_id:
        # Return status for all configured devices
        all_status = {}
        for device in config.get('devices', []):
            dev_id = device['device_id']
            
            # Try cache first
            cached = get_cached_status(dev_id)
            if cached:
                all_status[dev_id] = translate_to_legacy_format(cached)
            else:
                # Fetch from API
                status = fetch_device_status(dev_id)
                if status:
                    all_status[dev_id] = translate_to_legacy_format(status)
        
        return jsonify(all_status)
    
    # Get status for specific device
    # Try cache first (MQTT updates)
    cached = get_cached_status(device_id)
    if cached:
        return jsonify(translate_to_legacy_format(cached))
    
    # Fetch from Cloud API
    status = fetch_device_status(device_id)
    if status:
        return jsonify(translate_to_legacy_format(status))
    
    return jsonify({"error": "Device not found"}), 404


@app.route('/api/v1/print', methods=['GET'])
def get_print_status():
    """Legacy endpoint: Get print status"""
    return get_status()


@app.route('/api/v1/devices', methods=['GET'])
def list_devices():
    """List all configured devices"""
    if not api_client:
        return jsonify({"error": "API client not initialized"}), 500
    
    try:
        devices = api_client.get_devices()
        return jsonify({
            "devices": [Device.from_dict(d).to_dict() for d in devices]
        })
    except BambuAPIError as e:
        return jsonify({"error": str(e)}), 502


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api_client": "initialized" if api_client else "not initialized",
        "mqtt_bridge": "running" if mqtt_bridge else "stopped",
        "devices": len(config.get('devices', [])),
        "timestamp": format_timestamp()
    })


def main():
    """Main entry point"""
    print("=" * 80)
    print("Bambu Lab Compatibility Layer Server")
    print("=" * 80)
    print()
    
    # Load configuration
    load_config()
    
    # Initialize API client
    if not init_api_client():
        print("ERROR: Failed to initialize API client")
        print("Please check your configuration and token")
        return 1
    
    # Initialize MQTT bridge
    init_mqtt_bridge()
    
    # Print configuration
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8080)
    
    print(f"Devices: {len(config.get('devices', []))}")
    print(f"API Client: Initialized")
    print(f"MQTT Bridge: {'Running' if mqtt_bridge else 'Disabled'}")
    print()
    print(f"Starting server on http://{host}:{port}")
    print("=" * 80)
    print()
    
    # Run server
    try:
        app.run(host=host, port=port, debug=False)
    finally:
        # Cleanup
        if mqtt_bridge:
            mqtt_bridge.stop()
            logger.info("MQTT bridge stopped")


if __name__ == '__main__':
    sys.exit(main())
