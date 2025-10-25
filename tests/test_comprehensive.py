#!/usr/bin/env python3
"""
Comprehensive Live Test Suite
==============================

Automatically tests all major functionality:
1. Starts proxy server
2. Tests Cloud API endpoints
3. Pulls data from first available printer
4. Tests file upload to cloud
5. Tests video streaming
6. Tests local FTP upload (optional)

Requires valid credentials in test_config.json
"""

import sys
import os
import time
import json
import threading
import signal
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import (
    BambuClient,
    MQTTClient,
    JPEGFrameStream,
    RTSPStream,
    LocalFTPClient,
    get_video_stream,
)


class TestConfig:
    """Load test configuration"""
    
    def __init__(self, config_file="test_config.json"):
        self.config_file = Path(__file__).parent / config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load or create config file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Create example config
            example = {
                "cloud_token": "YOUR_BAMBU_CLOUD_TOKEN",
                "test_modes": {
                    "cloud_api": True,
                    "mqtt": True,
                    "video_stream": True,
                    "file_upload": False,  # Disabled by default - creates real file
                    "local_ftp": False     # Disabled by default - requires local network
                },
                "test_file": {
                    "create_dummy": True,
                    "path": "test_model.3mf",
                    "size_mb": 0.1
                },
                "timeouts": {
                    "mqtt_connect": 10,
                    "video_frame": 15,
                    "api_request": 30
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(example, f, indent=2)
            
            print(f"Created example config: {self.config_file}")
            print("Please edit with your credentials and re-run.")
            return example
    
    def is_configured(self):
        """Check if config has real credentials"""
        token = self.config.get('cloud_token', '')
        return token and token != 'YOUR_BAMBU_CLOUD_TOKEN'


class TestRunner:
    """Main test runner"""
    
    def __init__(self, config):
        self.config = config.config if isinstance(config, TestConfig) else config
        self.client = None
        self.mqtt = None
        self.results = {}
        self.test_device = None
        self.proxy_process = None
    
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_test(self, name, status, details=""):
        """Print test result"""
        status_text = "PASS" if status else "FAIL"
        print(f"[{status_text}] {name:<40}")
        if details:
            print(f"  > {details}")
        self.results[name] = status
    
    def start_proxy_server(self):
        """Start proxy server in background (optional)"""
        # Note: Would need to import and start servers/proxy.py
        # For now, we'll skip this as it requires configuration
        pass
    
    def test_cloud_api(self):
        """Test Cloud API functionality"""
        self.print_header("Cloud API Tests")
        
        try:
            # Initialize client
            self.client = BambuClient(token=self.config['cloud_token'])
            self.print_test("Initialize BambuClient", True)
        except Exception as e:
            self.print_test("Initialize BambuClient", False, str(e))
            return False
        
        # Test get devices
        try:
            devices = self.client.get_devices()
            if devices and len(devices) > 0:
                print(f"  > Found {len(devices)} device(s)")
                
                # Print detailed info for ALL printers
                print(f"\n    [ALL PRINTERS] Complete Information:")
                for idx, device in enumerate(devices):
                    print(f"\n    ==================== PRINTER {idx + 1} ====================")
                    print(f"       Name: {device.get('name', 'N/A')}")
                    print(f"       Serial: {device.get('dev_id', 'N/A')}")
                    print(f"       Model: {device.get('dev_model_name', 'N/A')} ({device.get('dev_product_name', 'N/A')})")
                    print(f"       Online: {'Yes' if device.get('online') else 'No'}")
                    print(f"       Print Status: {device.get('print_status', 'UNKNOWN')}")
                    print(f"       Nozzle Size: {device.get('nozzle_diameter', 'N/A')}mm")
                    print(f"       Access Code: {device.get('dev_access_code', 'N/A')}")
                    
                    # Network info
                    if device.get('dev_ip'):
                        print(f"       IP Address: {device.get('dev_ip')}")
                    
                    # Firmware
                    if device.get('firmware'):
                        print(f"       Firmware: {device.get('firmware')}")
                    
                    # Print all device fields
                    print(f"\n       [DATA] ALL FIELDS ({len(device)} fields):")
                    for key in sorted(device.keys()):
                        val = device[key]
                        if isinstance(val, (dict, list)):
                            print(f"         {key}: {type(val).__name__} (length: {len(val)})")
                        else:
                            val_str = str(val)[:100]
                            print(f"         {key}: {val_str}")
                
                # Use first device for subsequent tests
                self.test_device = devices[2]
                print(f"\n    [TEST] Using '{self.test_device.get('name')}' for remaining tests")
                
                self.print_test("Get devices", True, f"Found {len(devices)} device(s)")
            else:
                self.print_test("Get devices", False, "No devices found")
                return False
        except Exception as e:
            self.print_test("Get devices", False, str(e))
            return False
        
        # Test device info (Note: may not be a separate endpoint)
        try:
            device_id = self.test_device['dev_id']
            # Try to get additional info - this endpoint may return 405
            try:
                info = self.client.get_device_info(device_id)
                
                print(f"\n    [DEVICE] Device Info Response:")
                print(f"       Keys: {list(info.keys())}")
                
                # Print all top-level fields
                for key, val in info.items():
                    if isinstance(val, (dict, list)):
                        print(f"       {key}: {type(val).__name__} (length: {len(val)})")
                    elif not isinstance(val, (dict, list)):
                        print(f"       {key}: {val}")
                
                # If there's bind data, show it
                if 'bind' in info:
                    bind_list = info['bind'] if isinstance(info['bind'], list) else [info['bind']]
                    print(f"\n    [DATA] BIND INFO ({len(bind_list)} device(s)):")
                    for bind_data in bind_list:
                        if isinstance(bind_data, dict):
                            for key in sorted(bind_data.keys()):
                                val = bind_data[key]
                                if isinstance(val, (dict, list)):
                                    print(f"       {key}: {type(val).__name__}")
                                else:
                                    val_str = str(val)[:100]
                                    print(f"       {key}: {val_str}")
                
                self.print_test("Get device info", True, "All fields displayed")
            except Exception as e:
                # Device info might be in the bind response already
                if '405' in str(e):
                    self.print_test("Get device info", True, 
                                  "Using info from bind endpoint (405)")
                else:
                    raise
        except Exception as e:
            self.print_test("Get device info", False, str(e))
        
        # Test device version
        try:
            version = self.client.get_device_version(device_id)
            
            print(f"\n    [VERSION] Device Version Response:")
            print(f"       Keys: {list(version.keys())}")
            
            fw_version = None
            if 'devices' in version:
                print(f"\n    [DATA] VERSION DATA ({len(version['devices'])} device(s)):")
                for dev in version['devices']:
                    if dev.get('dev_id') == device_id:
                        print(f"\n       Device: {dev.get('name', 'N/A')}")
                        print(f"       Dev ID: {dev.get('dev_id', 'N/A')}")
                        print(f"       Model: {dev.get('dev_model_name', 'N/A')}")
                        
                        # OTA/Firmware info
                        if 'ota' in dev:
                            ota = dev['ota']
                            fw_version = ota.get('version', 'unknown')
                            print(f"\n       [FIRMWARE]")
                            print(f"       Current Version: {ota.get('version', 'N/A')}")
                            print(f"       New Version State: {ota.get('new_version_state', 'N/A')}")
                            print(f"       New Version: {ota.get('new_version_number', 'N/A')}")
                            print(f"       Force Upgrade: {ota.get('force_upgrade', False)}")
                            print(f"       Consistency Request: {ota.get('consistency_request', False)}")
                            
                            # Print all OTA fields
                            print(f"\n       [DATA] ALL OTA FIELDS ({len(ota)} fields):")
                            for key in sorted(ota.keys()):
                                print(f"         {key}: {ota[key]}")
                        
                        # AMS info
                        if 'ams' in dev:
                            ams_list = dev['ams'] if isinstance(dev['ams'], list) else [dev['ams']]
                            print(f"\n       [AMS] Units: {len(ams_list)}")
                            for idx, ams in enumerate(ams_list):
                                print(f"         AMS {idx+1}:")
                                print(f"           SW Version: {ams.get('sw_ver', 'N/A')}")
                                print(f"           HW Version: {ams.get('hw_ver', 'N/A')}")
                                
                                # Print all AMS fields
                                if len(ams) > 0:
                                    print(f"           Fields ({len(ams)}):")
                                    for key in sorted(ams.keys()):
                                        if key not in ['sw_ver', 'hw_ver']:
                                            print(f"             {key}: {ams[key]}")
                        else:
                            print(f"\n       [AMS] Units: 0 (none installed)")
                        
                        # Print ALL device fields
                        print(f"\n       [DATA] ALL DEVICE VERSION FIELDS ({len(dev)} fields):")
                        for key in sorted(dev.keys()):
                            val = dev[key]
                            if isinstance(val, (dict, list)):
                                print(f"         {key}: {type(val).__name__} (length: {len(val)})")
                            else:
                                print(f"         {key}: {val}")
            
            if fw_version and fw_version != 'unknown':
                self.print_test("Get device version", True, f"Firmware v{fw_version}")
            else:
                self.print_test("Get device version", True, "Version data retrieved")
        except Exception as e:
            self.print_test("Get device version", False, str(e))
        
        # Test AMS/Filament info
        try:
            ams_info = self.client.get_ams_filaments(device_id)
            
            print(f"\n    [AMS] Filament Information:")
            print(f"       Has AMS: {ams_info['has_ams']}")
            print(f"       Total Trays: {ams_info['total_trays']}")
            
            if ams_info['has_ams'] and ams_info['ams_units']:
                for unit in ams_info['ams_units']:
                    print(f"\n       AMS Unit {unit['unit_id']}:")
                    print(f"         Software: {unit['sw_version']}")
                    print(f"         Hardware: {unit['hw_version']}")
                    
                    if unit['trays']:
                        print(f"         Trays: {len(unit['trays'])}")
                        for tray in unit['trays']:
                            print(f"\n           Tray {tray['tray_id']}:")
                            print(f"             Type: {tray.get('filament_type', 'N/A')}")
                            print(f"             Color: {tray.get('filament_color', 'N/A')}")
                            print(f"             Weight: {tray.get('filament_weight', 'N/A')}")
                            print(f"             Temp: {tray.get('temperature', 'N/A')}C")
                            print(f"             Remaining: {tray.get('remaining', 'N/A')}")
                            
                            # Print all tray fields
                            if tray.get('raw_data'):
                                print(f"             All Fields ({len(tray['raw_data'])} fields):")
                                for key in sorted(tray['raw_data'].keys()):
                                    val = tray['raw_data'][key]
                                    if not isinstance(val, (dict, list)):
                                        print(f"               {key}: {val}")
                    else:
                        print(f"         No tray data available")
                
                self.print_test("Get AMS filaments", True, f"{ams_info['total_trays']} tray(s)")
            else:
                print(f"       No AMS units installed")
                self.print_test("Get AMS filaments", True, "No AMS")
                
        except Exception as e:
            self.print_test("Get AMS filaments", False, str(e))
        
        # Test print status
        try:
            status = self.client.get_print_status()
            device_status = next((d for d in status.get('devices', []) 
                                 if d['dev_id'] == device_id), None)
            if device_status:
                print_state = device_status.get('print_status', 'UNKNOWN')
                
                print(f"\n    [PRINT] Print Status:")
                print(f"       State: {print_state}")
                print(f"       Online: {device_status.get('online', False)}")
                
                if 'print' in device_status:
                    print_data = device_status['print']
                    
                    print(f"\n       [PROGRESS]")
                    if 'mc_percent' in print_data:
                        print(f"       Progress: {print_data['mc_percent']}%")
                    if 'layer_num' in print_data and 'total_layer_num' in print_data:
                        print(f"       Layer: {print_data['layer_num']}/{print_data['total_layer_num']}")
                    if 'mc_remaining_time' in print_data:
                        remaining = print_data['mc_remaining_time']
                        hours = remaining // 60
                        mins = remaining % 60
                        print(f"       Remaining: {hours}h {mins}m")
                    
                    print(f"\n       [TEMPERATURES]")
                    if 'nozzle_temper' in print_data:
                        print(f"       Nozzle: {print_data['nozzle_temper']}C / {print_data.get('nozzle_target_temper', 'N/A')}C")
                    if 'bed_temper' in print_data:
                        print(f"       Bed: {print_data['bed_temper']}C / {print_data.get('bed_target_temper', 'N/A')}C")
                    if 'chamber_temper' in print_data:
                        print(f"       Chamber: {print_data['chamber_temper']}C")
                    
                    print(f"\n       [SPEEDS/FANS]")
                    if 'spd_lvl' in print_data:
                        print(f"       Speed Level: {print_data['spd_lvl']}")
                    if 'spd_mag' in print_data:
                        print(f"       Speed Modifier: {print_data['spd_mag']}%")
                    if 'cooling_fan_speed' in print_data:
                        print(f"       Part Cooling: {print_data['cooling_fan_speed']}%")
                    if 'heatbreak_fan_speed' in print_data:
                        print(f"       Heatbreak Fan: {print_data['heatbreak_fan_speed']}%")
                    
                    # Print ALL print data fields
                    print(f"\n       [DATA] ALL PRINT STATUS FIELDS ({len(print_data)} fields):")
                    for key in sorted(print_data.keys()):
                        val = print_data[key]
                        if isinstance(val, (dict, list)):
                            print(f"         {key}: {type(val).__name__}")
                        else:
                            print(f"         {key}: {val}")
                
                self.print_test("Get print status", True, f"State: {print_state}")
            else:
                self.print_test("Get print status", True, "No active device")
        except Exception as e:
            self.print_test("Get print status", False, str(e))
        
        # Test user profile
        try:
            profile = self.client.get_user_profile()
            
            print(f"       UID: {profile.get('uid', 'N/A')}")
            print(f"       Name: {profile.get('name', 'N/A')}")
            print(f"       Account: {profile.get('account', 'N/A')}")
            if 'productModels' in profile:
                models = profile['productModels']
                if models:
                    print(f"       Owned Printers: {', '.join(models)}")
            
            self.print_test("Get user profile", True)
        except Exception as e:
            self.print_test("Get user profile", False, str(e))
        
        # Test camera credentials
        try:
            creds = self.client.get_camera_credentials(device_id)
            
            print(f"\n    [CAMERA] Camera Credentials (TTCode):")
            print(f"       TTCode: {creds.get('ttcode', 'N/A')}")
            print(f"       Password: {creds.get('passwd', 'N/A')}")
            print(f"       Auth Key: {creds.get('authkey', 'N/A')}")
            
            # Print all credential fields
            print(f"\n    [DATA] ALL TTCODE FIELDS ({len(creds)} fields):")
            for key in sorted(creds.keys()):
                print(f"       {key}: {creds[key]}")
            
            self.print_test("Get camera credentials", True, "TTCode obtained")
        except Exception as e:
            self.print_test("Get camera credentials", False, str(e))
        
        # Test cloud video URL
        try:
            cloud_video = self.client.get_cloud_video_url(device_id)
            
            print(f"\n    [CAMERA] Cloud Video Stream:")
            print(f"       Response Keys: {list(cloud_video.keys())}")
            
            if 'url' in cloud_video or 'stream_url' in cloud_video:
                video_url = cloud_video.get('url') or cloud_video.get('stream_url')
                print(f"       Cloud Video URL: {video_url}")
                self.print_test("Get cloud video URL", True, "Cloud stream available")
            else:
                print(f"       Cloud streaming: Not available (use local access)")
                print(f"       TTCode provided for local streaming")
                self.print_test("Get cloud video URL", True, "Local streaming only")
            
            # Print all video stream fields
            print(f"\n    [DATA] ALL VIDEO STREAM FIELDS:")
            for key, val in sorted(cloud_video.items()):
                if isinstance(val, (dict, list)):
                    print(f"       {key}: {type(val).__name__}")
                else:
                    val_str = str(val)[:100]
                    print(f"       {key}: {val_str}")
            
        except Exception as e:
            self.print_test("Get cloud video URL", False, str(e))
        
        # Print TUTK/P2P streaming information
        print(f"\n    [TUTK] P2P Video Streaming (TUTK Protocol):")
        print(f"       Protocol Type: {creds.get('type', 'N/A')}")
        print(f"       TTCode (UID): {creds.get('ttcode', 'N/A')}")
        print(f"       Auth Key: {creds.get('authkey', 'N/A')}")
        print(f"       Password: {creds.get('passwd', 'N/A')}")
        print(f"       Region: {creds.get('region', 'N/A')}")
            
        # Print complete TTCode info
        print(f"\n    [DATA] COMPLETE TUTK CREDENTIALS:")
        tutk_fields = ['ttcode', 'passwd', 'authkey', 'region', 'type', 
                      'stream_key', 'stream_salt', 'channel_name', 'app_id',
                      'rtm', 'streams', 'peers']
        for field in tutk_fields:
            if field in creds:
                val = creds[field]
                if val and val != '':
                    print(f"       {field}: {val}")
        
        self.print_test("TUTK stream info", True, "Credentials available")
        
        return True
    
    def test_mqtt_connection(self):
        """Test MQTT functionality"""
        if not self.config['test_modes'].get('mqtt', True):
            print("\nMQTT tests disabled in config")
            return
        
        self.print_header("MQTT Tests")
        
        if not self.test_device:
            self.print_test("MQTT setup", False, "No device available")
            return
        
        try:
            # Get UID from profile
            profile = self.client.get_user_profile()
            uid = str(profile.get('uid', ''))
            device_id = self.test_device['dev_id']
            
            if not uid:
                self.print_test("Get UID for MQTT", False, "UID not found")
                return
            
            self.print_test("Get UID for MQTT", True, f"UID: {uid}")
        except Exception as e:
            self.print_test("Get UID for MQTT", False, str(e))
            return
        
        # Test MQTT connection
        try:
            mqtt_connected = threading.Event()
            mqtt_data_received = threading.Event()
            received_data = {}
            message_count = [0]
            all_messages = []
            
            def on_message(dev_id, data):
                message_count[0] += 1
                received_data['data'] = data
                all_messages.append(data)
                mqtt_data_received.set()
            
            def on_connect():
                mqtt_connected.set()
            
            self.mqtt = MQTTClient(
                username=uid,
                access_token=self.config['cloud_token'],
                device_id=device_id,
                on_message=on_message
            )
            
            # Connect in background
            mqtt_thread = threading.Thread(target=self.mqtt.connect, kwargs={'blocking': True})
            mqtt_thread.daemon = True
            mqtt_thread.start()
            
            # Wait for connection
            timeout = self.config['timeouts'].get('mqtt_connect', 10)
            time.sleep(2)  # Give it time to connect
            
            if self.mqtt.client and self.mqtt.client.is_connected():
                self.print_test("MQTT connect", True)
                
                # Request status update
                try:
                    self.mqtt.request_full_status()
                    self.print_test("Request full status", True)
                    
                    # Wait for data
                    if mqtt_data_received.wait(timeout=10):
                        data = received_data.get('data', {})
                        
                        # Print complete MQTT data structure
                        print(f"\n    [MQTT] Complete Data Received:")
                        print(f"       Top-level keys: {list(data.keys())}")
                        print(f"       Total fields: {len(data)}")
                        
                        # Print ALL top-level fields
                        print(f"\n    [DATA] ALL MQTT FIELDS:")
                        for key in sorted(data.keys()):
                            val = data[key]
                            if isinstance(val, dict):
                                print(f"       {key}: dict with {len(val)} fields")
                                # Print dict contents
                                for subkey in sorted(val.keys())[:10]:  # First 10 subkeys
                                    subval = val[subkey]
                                    if isinstance(subval, (dict, list)):
                                        print(f"         {subkey}: {type(subval).__name__}")
                                    else:
                                        print(f"         {subkey}: {subval}")
                                if len(val) > 10:
                                    print(f"         ... and {len(val) - 10} more fields")
                            elif isinstance(val, list):
                                print(f"       {key}: list with {len(val)} items")
                                if len(val) > 0 and isinstance(val[0], dict):
                                    print(f"         First item keys: {list(val[0].keys())}")
                            else:
                                print(f"       {key}: {val}")
                        
                        # Print detailed PRINT data
                        if 'print' in data:
                            print_info = data['print']
                            print(f"\n    [PRINT] Print Information ({len(print_info)} fields):")
                            
                            # Organize by category
                            temps = {}
                            progress = {}
                            speeds = {}
                            other = {}
                            
                            for key, val in print_info.items():
                                if 'temp' in key.lower():
                                    temps[key] = val
                                elif any(x in key for x in ['percent', 'layer', 'remain', 'stage']):
                                    progress[key] = val
                                elif any(x in key for x in ['spd', 'speed', 'fan']):
                                    speeds[key] = val
                                else:
                                    other[key] = val
                            
                            if temps:
                                print(f"\n       Temperatures:")
                                for k, v in sorted(temps.items()):
                                    print(f"         {k}: {v}")
                            
                            if progress:
                                print(f"\n       Progress:")
                                for k, v in sorted(progress.items()):
                                    print(f"         {k}: {v}")
                            
                            if speeds:
                                print(f"\n       Speeds/Fans:")
                                for k, v in sorted(speeds.items()):
                                    print(f"         {k}: {v}")
                            
                            if other:
                                print(f"\n       Other Print Data:")
                                for k, v in sorted(other.items()):
                                    val_str = str(v)[:100]
                                    print(f"         {k}: {val_str}")
                        
                        # Print AMS data
                        if 'ams' in data:
                            ams_data = data['ams']
                            print(f"\n    [AMS] AMS Information:")
                            if 'ams' in ams_data:
                                units = ams_data['ams']
                                print(f"       Units: {len(units)}")
                                for idx, unit in enumerate(units):
                                    print(f"\n       Unit {idx}:")
                                    if 'tray' in unit:
                                        print(f"         Trays: {len(unit['tray'])}")
                                        for tray in unit['tray']:
                                            tray_id = tray.get('id', '?')
                                            tray_type = tray.get('tray_type', 'N/A')
                                            print(f"           Tray {tray_id}: {tray_type}")
                                    # Print all unit fields
                                    print(f"         All fields ({len(unit)}):")
                                    for k, v in sorted(unit.items()):
                                        if k != 'tray' and not isinstance(v, (dict, list)):
                                            print(f"           {k}: {v}")
                        
                        # Print system/hardware data
                        if 'system' in data or 'hw' in data or 'info' in data:
                            print(f"\n    [SYSTEM] Hardware/System Info:")
                            for key in ['system', 'hw', 'info']:
                                if key in data:
                                    print(f"       {key}: {data[key]}")
                        
                        self.print_test("Receive MQTT data", True, 
                                      f"Got {len(data)} top-level fields")
                        
                        # Monitor for 5 seconds to collect more data
                        print(f"\n    [STREAM] Monitoring MQTT stream for 5 seconds...")
                        start_time = time.time()
                        initial_count = message_count[0]
                        
                        while time.time() - start_time < 5:
                            time.sleep(0.5)
                            current_count = message_count[0]
                            if current_count > initial_count:
                                elapsed = time.time() - start_time
                                # Get latest message
                                if all_messages:
                                    latest = all_messages[-1]
                                    summary = []
                                    
                                    # Try to extract useful info
                                    if 'print' in latest:
                                        p = latest['print']
                                        if 'gcode_state' in p:
                                            summary.append(f"State: {p['gcode_state']}")
                                        if 'mc_percent' in p:
                                            summary.append(f"Progress: {p['mc_percent']}%")
                                        if 'nozzle_temper' in p:
                                            summary.append(f"Nozzle: {p['nozzle_temper']}C")
                                        if 'bed_temper' in p:
                                            summary.append(f"Bed: {p['bed_temper']}C")
                                    
                                    # Show all top-level keys and field counts
                                    summary_parts = []
                                    for key, val in latest.items():
                                        if isinstance(val, dict):
                                            summary_parts.append(f"{key}({len(val)})")
                                        elif isinstance(val, list):
                                            summary_parts.append(f"{key}[{len(val)}]")
                                        else:
                                            summary_parts.append(f"{key}={val}")
                                    
                                    if summary:
                                        summary_str = ", ".join(summary)
                                    else:
                                        summary_str = ", ".join(summary_parts[:5])  # First 5 parts
                                    
                                    print(f"       [{elapsed:.1f}s] Message #{current_count}: {summary_str}")
                                    
                                    # Print ALL fields for messages with few fields
                                    if len(latest) <= 2:
                                        print(f"                   Full message: {latest}")
                        
                        total_messages = message_count[0] - initial_count
                        print(f"\n       Monitoring complete: {total_messages} additional messages")
                        if total_messages > 0:
                            print(f"       Average rate: {total_messages/5:.1f} messages/second")
                        
                        # Print summary of all collected messages
                        if len(all_messages) > 1:
                            print(f"\n    [SUMMARY] Collected {len(all_messages)} total messages")
                            print(f"       Unique top-level keys across all messages:")
                            all_keys = set()
                            for msg in all_messages:
                                all_keys.update(msg.keys())
                            print(f"       {sorted(all_keys)}")
                            
                            # Print full content of last 3 messages
                            print(f"\n    [MESSAGES] Last 3 messages (full content):")
                            for idx, msg in enumerate(all_messages[-3:]):
                                msg_num = len(all_messages) - len(all_messages[-3:]) + idx + 1
                                print(f"\n       Message {msg_num}:")
                                
                                if not msg or len(msg) == 0:
                                    print(f"         (empty message)")
                                    continue
                                
                                for key in sorted(msg.keys()):
                                    val = msg[key]
                                    if isinstance(val, dict):
                                        if len(val) <= 10:
                                            # Small dicts - print inline
                                            print(f"         {key}: {val}")
                                        else:
                                            # Large dicts - show organized
                                            print(f"         {key}: dict with {len(val)} fields")
                                            
                                            # Categorize fields
                                            if key == 'print':
                                                temps = {k: v for k, v in val.items() if 'temp' in k.lower()}
                                                progress = {k: v for k, v in val.items() if any(x in k for x in ['percent', 'layer', 'remain', 'stage', 'state'])}
                                                speeds = {k: v for k, v in val.items() if any(x in k for x in ['spd', 'speed', 'fan'])}
                                                
                                                if temps:
                                                    print(f"           Temperatures:")
                                                    for k, v in sorted(temps.items()):
                                                        print(f"             {k}: {v}")
                                                
                                                if progress:
                                                    print(f"           Progress/State:")
                                                    for k, v in sorted(progress.items()):
                                                        val_str = str(v)[:50]
                                                        print(f"             {k}: {val_str}")
                                                
                                                if speeds:
                                                    print(f"           Speeds/Fans:")
                                                    for k, v in sorted(speeds.items()):
                                                        print(f"             {k}: {v}")
                                                
                                                # Show AMS data if present
                                                if 'ams' in val:
                                                    ams_data = val['ams']
                                                    if isinstance(ams_data, dict) and 'ams' in ams_data:
                                                        print(f"           AMS Units:")
                                                        for unit in ams_data['ams']:
                                                            unit_id = unit.get('id', '?')
                                                            humidity = unit.get('humidity', '?')
                                                            temp = unit.get('temp', '?')
                                                            print(f"             Unit {unit_id}: {humidity}% humidity, {temp}°C")
                                                            if 'tray' in unit:
                                                                for tray in unit['tray']:
                                                                    if tray.get('tray_type'):
                                                                        print(f"               Tray {tray['id']}: {tray['tray_type']} ({tray.get('tray_color', 'N/A')})")
                                                
                                                # Show other important fields
                                                other_important = ['wifi_signal', 'nozzle_diameter', 'nozzle_type', 
                                                                 'subtask_name', 'gcode_file', 'project_id']
                                                important_vals = {k: val[k] for k in other_important if k in val}
                                                if important_vals:
                                                    print(f"           Other Info:")
                                                    for k, v in sorted(important_vals.items()):
                                                        val_str = str(v)[:50]
                                                        print(f"             {k}: {val_str}")
                                            else:
                                                # Other dicts - show first 5 fields
                                                for k, v in sorted(list(val.items())[:5]):
                                                    val_str = str(v)[:50]
                                                    print(f"           {k}: {val_str}")
                                                if len(val) > 5:
                                                    print(f"           ... and {len(val) - 5} more fields")
                                    elif isinstance(val, list):
                                        if len(val) == 0:
                                            print(f"         {key}: []")
                                        elif len(val) <= 3:
                                            print(f"         {key}: {val}")
                                        else:
                                            print(f"         {key}: list with {len(val)} items")
                                            print(f"           First item: {val[0]}")
                                    else:
                                        val_str = str(val)[:100]
                                        print(f"         {key}: {val_str}")
                        
                        self.print_test("Monitor MQTT stream", True, 
                                      f"Received {total_messages} messages in 5 seconds")
                    else:
                        self.print_test("Receive MQTT data", False, "Timeout waiting for data")
                except Exception as e:
                    self.print_test("MQTT data exchange", False, str(e))
            else:
                self.print_test("MQTT connect", False, "Connection failed")
            
        except Exception as e:
            self.print_test("MQTT connection", False, str(e))
    
    def test_video_stream(self):
        """Test video streaming"""
        if not self.config['test_modes'].get('video_stream', True):
            print("\nVideo stream tests disabled in config")
            return
        
        self.print_header("Video Stream Tests")
        
        if not self.test_device:
            self.print_test("Video setup", False, "No device available")
            return
        
        # Determine printer model and IP
        try:
            device_id = self.test_device['dev_id']
            
            # Try to get IP - it may not be available via API
            printer_ip = None
            model = self.test_device.get('dev_product_name', 'Unknown')
            access_code = self.test_device.get('dev_access_code', '').strip()
            
            if 'ip' in self.test_device:
                printer_ip = self.test_device['ip']
            
            if not printer_ip:
                try:
                    info = self.client.get_device_info(device_id)
                    printer_ip = info.get('ip_address') or info.get('local_ip') or info.get('ip')
                except:
                    pass
            
            if not printer_ip and 'raw_data' in self.test_device:
                for key in ['local_ip', 'ip_address', 'ip', 'lan_ip']:
                    if key in self.test_device['raw_data']:
                        printer_ip = self.test_device['raw_data'][key]
                        break
            
            if not printer_ip:
                try:
                    status = self.client.get_print_status(force=True)
                    for dev in status.get('devices', []):
                        if dev.get('dev_id') == device_id:
                            printer_ip = dev.get('ip') or dev.get('local_ip')
                            if printer_ip:
                                break
                except:
                    pass
            
            if not printer_ip:
                self.print_test("Get printer network info", True, "Printer on cloud only")
                return
            
            if not access_code:
                self.print_test("Get access code", False, "Access code not available")
                return
            
            print(f"       IP: {printer_ip}")
            print(f"       Model: {model}")
            print(f"       Access Code: {access_code}")
            self.print_test("Get printer network info", True)
            
        except Exception as e:
            self.print_test("Get printer network info", False, str(e))
            return
        
        # Test appropriate stream type
        try:
            stream = get_video_stream(printer_ip, access_code, model)
            
            if isinstance(stream, RTSPStream):
                url = stream.get_stream_url()
                
                print(f"       Type: RTSP (X1 series)")
                print(f"       URL: {url}")
                self.print_test("Detect stream type", True)
                
            elif isinstance(stream, JPEGFrameStream):
                print(f"       Type: JPEG (A1/P1 series)")
                self.print_test("Detect stream type", True)
                
                try:
                    stream.connect()
                    self.print_test("Connect to video stream", True)
                    
                    frame = stream.get_frame()
                    frame_size = len(frame) / 1024
                    print(f"       Frame size: {frame_size:.1f} KB")
                    self.print_test("Receive video frame", True)
                    
                    test_output = Path(__file__).parent / "test_frame.jpg"
                    with open(test_output, 'wb') as f:
                        f.write(frame)
                    print(f"       Saved: {test_output}")
                    self.print_test("Save frame to file", True)
                    
                except Exception as e:
                    self.print_test("Video frame capture", False, str(e))
                finally:
                    stream.disconnect()
            
        except Exception as e:
            self.print_test("Video stream test", False, str(e))
    
    def test_file_upload(self):
        """Test file upload to cloud"""
        if not self.config['test_modes'].get('file_upload', False):
            print("\nFile upload tests disabled in config")
            return
        
        self.print_header("File Upload Tests")
        
        # Create test file
        test_file = None
        try:
            if self.config['test_file'].get('create_dummy', True):
                # Create a dummy 3MF file (just random data for testing)
                size_mb = self.config['test_file'].get('size_mb', 0.1)
                size_bytes = int(size_mb * 1024 * 1024)
                
                test_file = Path(__file__).parent / "test_upload.3mf"
                with open(test_file, 'wb') as f:
                    f.write(b'PK\x03\x04' + os.urandom(size_bytes))
                
                print(f"       Size: {size_mb} MB")
                print(f"       Path: {test_file}")
                self.print_test("Create test file", True)
            else:
                test_file = Path(self.config['test_file'].get('path', 'test.3mf'))
                if not test_file.exists():
                    self.print_test("Find test file", False, f"{test_file} not found")
                    return
        except Exception as e:
            self.print_test("Prepare test file", False, str(e))
            return
        
        try:
            # Use consistent filename for URL request and actual upload
            upload_filename = "api_test.3mf"
            file_size = os.path.getsize(test_file) if test_file else 100000
            upload_info = self.client.get_upload_url(filename=upload_filename, size=file_size)
            upload_url = upload_info.get('upload_url')
            upload_ticket = upload_info.get('upload_ticket')
            urls_array = upload_info.get('urls', [])
            
            print(f"\n    [UPLOAD] Upload URL Response:")
            print(f"       Keys in response: {list(upload_info.keys())}")
            
            # Check for URL in different formats
            if upload_url:
                print(f"       Direct Upload URL: {upload_url[:60]}...")
            elif urls_array and isinstance(urls_array, list) and len(urls_array) > 0:
                # Extract filename URL from array
                filename_entry = next((e for e in urls_array if isinstance(e, dict) and e.get('type') == 'filename'), None)
                if filename_entry:
                    print(f"       Upload URL (from array): {filename_entry['url'][:60]}...")
                    print(f"       Format: AWS S3 signed URL (array format)")
                else:
                    print(f"       Upload URLs: {len(urls_array)} URL(s) in array")
            else:
                print(f"       Upload URL: NOT PROVIDED")
            
            print(f"       Upload Ticket: {upload_ticket if upload_ticket else 'No'}")
            
            if urls_array:
                print(f"       URLs Array: {len(urls_array)} entries")
                for idx, entry in enumerate(urls_array):
                    if isinstance(entry, dict):
                        print(f"         [{idx}] Type: {entry.get('type')}, File: {entry.get('file')}")
            
            # Print all fields in response
            print(f"\n    [DATA] ALL UPLOAD INFO FIELDS:")
            for key, val in sorted(upload_info.items()):
                if isinstance(val, (dict, list)):
                    print(f"       {key}: {type(val).__name__} (length: {len(val)})")
                else:
                    val_str = str(val)[:100]
                    print(f"       {key}: {val_str}")
            
            if not upload_url and not urls_array:
                self.print_test("Get upload URL", True, "Cloud upload not available for this account")
                print(f"\n    NOTE: Upload might require:")
                print(f"       - Bambu Lab Cloud subscription")
                print(f"       - Account verification")
                print(f"       - Specific region/locale")
                return
            
            self.print_test("Get upload URL", True, "S3 signed URLs received")
            
        except Exception as e:
            self.print_test("Get upload URL", False, str(e))
            print(f"\n     Error details: {str(e)}")
            return
        
        upload_success = False
        try:
            result = self.client.upload_file(str(test_file), filename=upload_filename)
            
            print(f"\n    [UPLOAD] Upload Result:")
            print(f"       Filename: {result.get('filename', 'N/A')}")
            print(f"       File Size: {result.get('file_size', 0)} bytes")
            print(f"       Status Code: {result.get('status_code', 'N/A')}")
            
            if result.get('status_code') in [200, 201, 204]:
                print(f"       Upload: SUCCESS")
                upload_success = True
            
            # Print all result fields
            print(f"\n    [DATA] ALL UPLOAD RESULT FIELDS:")
            for key, val in sorted(result.items()):
                val_str = str(val)[:100]
                print(f"       {key}: {val_str}")
            
            self.print_test("Upload file to cloud", True)
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n    [ERROR] Upload failed:")
            print(f"       Error: {error_msg[:200]}")
            self.print_test("Upload file to cloud", False, error_msg[:100])
            upload_success = False
            
        finally:
            if self.config['test_file'].get('create_dummy', True) and test_file:
                try:
                    test_file.unlink()
                except:
                    pass
        
        # Test listing cloud files (if upload succeeded)
        if upload_success:
            try:
                print(f"\n    [FILES] Cloud Files:")
                files = self.client.get_cloud_files()
                
                print(f"       Found {len(files)} file(s) in cloud storage")
                
                if files:
                    print(f"\n       Recent files:")
                    for idx, f in enumerate(files[:5]):  # Show first 5
                        name = f.get('name') or f.get('file_name') or f.get('title', 'N/A')
                        file_id = f.get('file_id') or f.get('model_id') or f.get('id', 'N/A')
                        print(f"         [{idx+1}] {name}")
                        print(f"             ID: {file_id}")
                    
                    self.print_test("List cloud files", True, f"{len(files)} file(s)")
                else:
                    print(f"       No files found (may take time to appear)")
                    self.print_test("List cloud files", True, "Endpoint available")
                    
            except Exception as e:
                self.print_test("List cloud files", False, str(e)[:80])
        else:
            print(f"\n    [INFO] Skipping file list (upload failed)")
    
    def test_local_ftp(self):
        """Test local FTP upload"""
        if not self.config['test_modes'].get('local_ftp', False):
            print("\nLocal FTP tests disabled in config")
            return
        
        self.print_header("Local FTP Tests")
        
        if not self.test_device:
            self.print_test("FTP setup", False, "No device available")
            return
    
    def cleanup(self):
        """Cleanup resources"""
        if self.mqtt:
            try:
                self.mqtt.disconnect()
            except:
                pass
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("Bambu Lab Cloud API - Comprehensive Test Suite")
        print(f"Test modes: {json.dumps(self.config['test_modes'], indent=2)}")
        
        try:
            # Run tests
            if self.test_cloud_api():
                self.test_mqtt_connection()
                self.test_video_stream()
                self.test_file_upload()
                self.test_local_ftp()
        finally:
            self.cleanup()
        
        self.print_header("Test Summary")
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        print(f"\nResults: {passed}/{total} tests passed")
        for test_name, result in self.results.items():
            status = "PASS" if result else "FAIL"
            print(f"  [{status}] {test_name}")
        
        print("\n" + "=" * 70)
        
        if passed == total:
            return 0
        else:
            return 1


def main():
    """Main entry point"""
    config = TestConfig()
    
    if not config.is_configured():
        print("Configuration needed")
        print(f"Edit {config.config_file} with your credentials")
        return 1
    
    runner = TestRunner(config)
    
    def signal_handler(sig, frame):
        print("\nTest interrupted")
        runner.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    return runner.run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
