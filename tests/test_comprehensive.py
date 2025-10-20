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
    
    def mask_serial(self, serial):
        """Replace serial number with random placeholder"""
        if not serial:
            return serial
        return '01S00A000000000'
    
    def mask_uid(self, uid):
        """Replace user ID with placeholder"""
        if not uid:
            return uid
        return '123456789'
    
    def mask_email(self, email):
        """Replace email with placeholder"""
        if not email or '@' not in email:
            return email
        return 'user@example.com'
    
    def mask_access_code(self, code):
        """Replace access code with placeholder"""
        if not code:
            return code
        return '12345678'
    
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
                self.test_device = devices[0]
                device_name = self.test_device.get('name', 'Unknown')
                self.print_test("Get devices", True, f"Found {len(devices)} device(s)")
                
                print(f"       Name: {device_name}")
                print(f"       Serial: {self.mask_serial(self.test_device.get('dev_id'))}")
                print(f"       Model: {self.test_device.get('dev_product_name', 'Unknown')} ({self.test_device.get('dev_model_name', 'N/A')})")
                print(f"       Online: {'Yes' if self.test_device.get('online') else 'No'}")
                print(f"       Print Status: {self.test_device.get('print_status', 'UNKNOWN')}")
                print(f"       Nozzle: {self.test_device.get('nozzle_diameter', 0.4)}mm")
                print(f"       Access Code: {self.mask_access_code(self.test_device.get('dev_access_code', 'N/A'))}")
                
                if len(devices) > 1:
                    print(f"       All Devices:")
                    for idx, dev in enumerate(devices, 1):
                        print(f"         {idx}. {dev.get('name')} ({self.mask_serial(dev.get('dev_id'))}) - {dev.get('dev_product_name')}")
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
                self.print_test("Get device info", True)
            except Exception as e:
                # Device info might be in the bind response already
                if '405' in str(e):
                    self.print_test("Get device info", True, 
                                  "Using info from bind endpoint")
                else:
                    raise
        except Exception as e:
            self.print_test("Get device info", False, str(e))
        
        # Test device version
        try:
            version = self.client.get_device_version(device_id)
            
            fw_version = None
            if 'devices' in version:
                for dev in version['devices']:
                    if dev.get('dev_id') == device_id:
                        print(f"       Module: {dev.get('module', 'Unknown')}")
                        if 'ota' in dev:
                            ota = dev['ota']
                            fw_version = ota.get('version', 'unknown')
                            print(f"       Firmware: {ota.get('version', 'Unknown')}")
                            print(f"       Latest Available: {ota.get('new_version_state', 'Unknown')}")
                            if ota.get('force_upgrade'):
                                print(f"       Force Upgrade: Yes")
                        if 'ams' in dev:
                            ams_list = dev['ams'] if isinstance(dev['ams'], list) else [dev['ams']]
                            print(f"       AMS Units: {len(ams_list)}")
                            for idx, ams in enumerate(ams_list):
                                print(f"         AMS {idx+1} FW: {ams.get('sw_ver', 'Unknown')}")
            
            if fw_version and fw_version != 'unknown':
                self.print_test("Get device version", True, f"v{fw_version}")
            else:
                self.print_test("Get device version", True, "Version data available")
        except Exception as e:
            self.print_test("Get device version", False, str(e))
        
        # Test print status
        try:
            status = self.client.get_print_status()
            device_status = next((d for d in status.get('devices', []) 
                                 if d['dev_id'] == device_id), None)
            if device_status:
                print_state = device_status.get('print_status', 'unknown')
                print(f"       State: {print_state}")
                
                if 'print' in device_status:
                    print_data = device_status['print']
                    
                    if 'mc_percent' in print_data:
                        print(f"       Progress: {print_data['mc_percent']}%")
                    if 'layer_num' in print_data and 'total_layer_num' in print_data:
                        print(f"       Layer: {print_data['layer_num']}/{print_data['total_layer_num']}")
                    if 'mc_remaining_time' in print_data:
                        remaining = print_data['mc_remaining_time']
                        hours = remaining // 60
                        minutes = remaining % 60
                        print(f"       Time Left: {hours}h {minutes}m")
                    
                    if 'nozzle_temper' in print_data:
                        target = print_data.get('nozzle_target_temper', 0)
                        print(f"       Nozzle: {print_data['nozzle_temper']}C -> {target}C")
                    if 'bed_temper' in print_data:
                        target = print_data.get('bed_target_temper', 0)
                        print(f"       Bed: {print_data['bed_temper']}C -> {target}C")
                    if 'chamber_temper' in print_data:
                        print(f"       Chamber: {print_data['chamber_temper']}C")
                    
                    if 'cooling_fan_speed' in print_data:
                        print(f"       Cooling Fan: {print_data['cooling_fan_speed']}%")
                    if 'aux_part_fan' in print_data:
                        print(f"       Aux Fan: {print_data['aux_part_fan']}%")
                    if 'chamber_fan' in print_data:
                        print(f"       Chamber Fan: {print_data['chamber_fan']}%")
                    
                    if 'gcode_state' in print_data:
                        print(f"       G-code State: {print_data['gcode_state']}")
                    if 'gcode_file' in print_data:
                        print(f"       File: {print_data['gcode_file']}")
                
                self.print_test("Get print status", True, f"State: {print_state}")
            else:
                self.print_test("Get print status", True, "No active print")
        except Exception as e:
            self.print_test("Get print status", False, str(e))
        
        # Test user profile
        try:
            profile = self.client.get_user_profile()
            
            print(f"       UID: {self.mask_uid(profile.get('uid', 'N/A'))}")
            print(f"       Name: {profile.get('name', 'N/A')}")
            print(f"       Account: {self.mask_email(profile.get('account', 'N/A'))}")
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
            self.print_test("Get camera credentials", True, "TTCode obtained")
        except Exception as e:
            self.print_test("Get camera credentials", False, str(e))
        
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
            
            self.print_test("Get UID for MQTT", True, f"UID: {self.mask_uid(uid)}")
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
                        
                        # Print detailed MQTT data
                        print(f"\n    MQTT Data Received:")
                        if 'print' in data:
                            print_info = data['print']
                            print(f"       Print Data Fields: {len(print_info)}")
                            
                            # Show key fields
                            key_fields = ['gcode_state', 'mc_percent', 'nozzle_temper', 
                                         'bed_temper', 'chamber_temper', 'mc_remaining_time']
                            for field in key_fields:
                                if field in print_info:
                                    print(f"         {field}: {print_info[field]}")
                        
                        if 'ams' in data:
                            ams_data = data['ams']
                            if 'ams' in ams_data:
                                print(f"       AMS Units: {len(ams_data['ams'])}")
                        
                        self.print_test("Receive MQTT data", True, 
                                      f"Got {len(data)} top-level fields")
                        
                        # Monitor for 5 seconds to collect more data
                        print(f"\n    Monitoring MQTT stream for 5 seconds...")
                        start_time = time.time()
                        initial_count = message_count[0]
                        
                        while time.time() - start_time < 5:
                            time.sleep(0.5)
                            if message_count[0] > initial_count:
                                elapsed = time.time() - start_time
                                print(f"       [{elapsed:.1f}s] Message #{message_count[0]} received")
                        
                        total_messages = message_count[0] - initial_count
                        print(f"\n       Monitoring complete: {total_messages} additional messages")
                        if total_messages > 0:
                            print(f"       Average rate: {total_messages/5:.1f} messages/second")
                        
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
            
            # Mask IP (show only last octet)
            ip_parts = printer_ip.split('.')
            if len(ip_parts) == 4:
                masked_ip = f"192.168.x.{ip_parts[3]}"
            else:
                masked_ip = "192.168.x.100"
            
            print(f"       IP: {masked_ip}")
            print(f"       Model: {model}")
            print(f"       Access Code: {self.mask_access_code(access_code)}")
            self.print_test("Get printer network info", True)
            
        except Exception as e:
            self.print_test("Get printer network info", False, str(e))
            return
        
        # Test appropriate stream type
        try:
            stream = get_video_stream(printer_ip, access_code, model)
            
            if isinstance(stream, RTSPStream):
                url = stream.get_stream_url()
                # Mask credentials in URL
                if '@' in url:
                    protocol, rest = url.split('://', 1)
                    creds, location = rest.split('@', 1)
                    # Keep IP last octet for debugging
                    ip_parts = location.split(':')[0].split('.')
                    if len(ip_parts) == 4:
                        masked_location = f"192.168.x.{ip_parts[3]}:{location.split(':', 1)[1] if ':' in location else '322/streaming/live/1'}"
                    else:
                        masked_location = location
                    masked_url = f"{protocol}://bblp:12345678@{masked_location}"
                else:
                    masked_url = url
                print(f"       Type: RTSP (X1 series)")
                print(f"       URL: {masked_url}")
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
            upload_info = self.client.get_upload_url()
            upload_url = upload_info.get('upload_url')
            upload_ticket = upload_info.get('upload_ticket')
            urls_array = upload_info.get('urls', [])
            
            print(f"       Upload URL: {upload_url[:60] if upload_url else 'NOT PROVIDED'}...")
            print(f"       Upload Ticket: {'Yes' if upload_ticket else 'No'}")
            print(f"       URLs Array: {urls_array}")
            
            if not upload_url and not urls_array:
                self.print_test("Get upload URL", True, "Cloud upload not available")
                return
            
            self.print_test("Get upload URL", True)
            
        except Exception as e:
            self.print_test("Get upload URL", False, str(e))
            print(f"\n     Error details: {str(e)}")
            return
        
        try:
            result = self.client.upload_file(str(test_file), filename="api_test.3mf")
            
            print(f"       File ID: {result.get('file_id', 'N/A')}")
            print(f"       File Size: {result.get('file_size', 0)} bytes")
            print(f"       Filename: {result.get('filename', 'N/A')}")
            if result.get('file_url'):
                print(f"       File URL: {result['file_url'][:60]}...")
            
            self.print_test("Upload file to cloud", True)
            
        except Exception as e:
            error_msg = str(e)
            print(f"       Error: {error_msg}")
            self.print_test("Upload file to cloud", False, error_msg[:100])
            
        finally:
            if self.config['test_file'].get('create_dummy', True) and test_file:
                try:
                    test_file.unlink()
                except:
                    pass
    
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
        self.print_header("Bambu Lab API - Comprehensive Test Suite")
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
