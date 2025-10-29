#!/usr/bin/env python3
"""
Comprehensive Integration Test
===============================

Tests all new features added to the bambulab library.
"""

import sys
import os

# Add repository root to path (two levels up from this file)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        from bambulab import (
            BambuClient,
            BambuAPIError,
            MQTTClient,
            MQTTBridge,
            TokenManager,
            Device,
            PrinterStatus,
            format_timestamp,
            parse_device_data,
            RTSPStream,
            JPEGFrameStream,
            VideoStreamError,
            get_video_stream,
            LocalFTPClient,
            LocalPrintClient,
            LocalAPIError,
            upload_and_print,
        )
        print("All imports successful")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False


def test_client_methods():
    """Test BambuClient has all expected methods"""
    print("\nTesting BambuClient methods...")
    from bambulab import BambuClient
    
    # Don't actually call methods, just verify they exist
    client = BambuClient("dummy_token")
    
    methods = [
        'get_devices',
        'get_device_version',
        'get_device_info',
        'get_print_status',
        'get_camera_credentials',
        'get_ttcode',
        'get_user_profile',
        'get_projects',
        'get_upload_url',
        'upload_file',  # NEW
    ]
    
    for method in methods:
        if not hasattr(client, method):
            print(f"Missing method: {method}")
            return False
        print(f"  {method}")
    
    print("All client methods present")
    return True


def test_video_classes():
    """Test video streaming classes"""
    print("\nTesting video streaming classes...")
    from bambulab import RTSPStream, JPEGFrameStream, get_video_stream
    
    # Test RTSPStream
    rtsp = RTSPStream("192.168.1.100", "12345678")
    url = rtsp.get_stream_url()
    if not url.startswith("rtsps://"):
        print(f"Invalid RTSP URL: {url}")
        return False
    print(f"  RTSPStream URL: {url}")
    
    # Test JPEGFrameStream (without connecting)
    jpeg = JPEGFrameStream("192.168.1.100", "12345678")
    if jpeg.printer_ip != "192.168.1.100":
        print("JPEGFrameStream initialization failed")
        return False
    print("  JPEGFrameStream initialized")
    
    # Test factory function
    stream_rtsp = get_video_stream("192.168.1.100", "12345678", "X1C")
    stream_jpeg = get_video_stream("192.168.1.100", "12345678", "P1P")
    
    if not isinstance(stream_rtsp, RTSPStream):
        print("Factory function returned wrong type for X1C")
        return False
    if not isinstance(stream_jpeg, JPEGFrameStream):
        print("Factory function returned wrong type for P1P")
        return False
    
    print("  Factory function works correctly")
    print("Video streaming classes OK")
    return True


def test_local_api_classes():
    """Test local API classes"""
    print("\nTesting local API classes...")
    from bambulab import LocalFTPClient, LocalPrintClient
    
    # Test LocalFTPClient initialization
    ftp = LocalFTPClient("192.168.1.100", "12345678")
    if ftp.printer_ip != "192.168.1.100":
        print("LocalFTPClient initialization failed")
        return False
    print("  LocalFTPClient initialized")
    
    # Test LocalPrintClient command generation
    cmd = LocalPrintClient.create_print_command("/model.3mf", use_ams=True)
    if cmd['print']['command'] != 'project_file':
        print("Print command generation failed")
        return False
    if not cmd['print']['use_ams']:
        print("Print command AMS setting incorrect")
        return False
    print("  LocalPrintClient command generation OK")
    
    # Test gcode command
    gcode_cmd = LocalPrintClient.create_gcode_print_command("/test.gcode")
    if gcode_cmd['print']['command'] != 'gcode_file':
        print("Gcode command generation failed")
        return False
    print("  LocalPrintClient gcode command OK")
    
    print("Local API classes OK")
    return True


def test_module_structure():
    """Test module structure and organization"""
    print("\nTesting module structure...")
    import bambulab
    
    # Check __all__ exports
    expected_exports = [
        'BambuClient',
        'BambuAPIError',
        'MQTTClient',
        'MQTTBridge',
        'TokenManager',
        'Device',
        'PrinterStatus',
        'format_timestamp',
        'parse_device_data',
        'RTSPStream',
        'JPEGFrameStream',
        'VideoStreamError',
        'get_video_stream',
        'LocalFTPClient',
        'LocalPrintClient',
        'LocalAPIError',
        'upload_and_print',
    ]
    
    for name in expected_exports:
        if name not in bambulab.__all__:
            print(f"Missing from __all__: {name}")
            return False
        if not hasattr(bambulab, name):
            print(f"Not exported: {name}")
            return False
    
    print(f"  All {len(expected_exports)} exports present")
    print("Module structure OK")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Bambu Lab Cloud API - Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_client_methods,
        test_video_classes,
        test_local_api_classes,
        test_module_structure,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
