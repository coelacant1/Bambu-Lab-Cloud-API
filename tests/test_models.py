#!/usr/bin/env python3
"""
Test Data Models
================

Tests for Device, PrinterStatus, and other data models.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab.models import Device, PrinterStatus, Project


def test_device_from_dict():
    """Test Device creation from dictionary"""
    print("Test: Device from dict...", end=" ")
    
    data = {
        "dev_id": "test123",
        "name": "Test Printer",
        "online": True,
        "print_status": "ACTIVE",
        "dev_model_name": "C11",
        "dev_product_name": "P1P",
        "dev_access_code": "12345678",
        "nozzle_diameter": 0.4,
        "dev_structure": "CoreXY"
    }
    
    device = Device.from_dict(data)
    assert device.dev_id == "test123"
    assert device.name == "Test Printer"
    assert device.online == True
    assert device.nozzle_diameter == 0.4
    print("PASSED")


def test_device_to_dict():
    """Test Device conversion to dictionary"""
    print("Test: Device to dict...", end=" ")
    
    device = Device(
        dev_id="test123",
        name="Test Printer",
        online=True,
        print_status="IDLE",
        dev_model_name="C11",
        dev_product_name="P1P",
        dev_access_code="12345678",
        nozzle_diameter=0.4,
        dev_structure="CoreXY"
    )
    
    data = device.to_dict()
    assert data["dev_id"] == "test123"
    assert data["name"] == "Test Printer"
    assert data["online"] == True
    print("PASSED")


def test_printer_status_from_mqtt():
    """Test PrinterStatus creation from MQTT data"""
    print("Test: PrinterStatus from MQTT...", end=" ")
    
    mqtt_data = {
        "print": {
            "nozzle_temper": 220.5,
            "nozzle_target_temper": 225.0,
            "bed_temper": 60.0,
            "bed_target_temper": 65.0,
            "mc_percent": 45,
            "gcode_state": "RUNNING",
            "layer_num": 50,
            "total_layer_num": 100
        }
    }
    
    status = PrinterStatus.from_mqtt("test_device", mqtt_data)
    assert status.device_id == "test_device"
    assert status.nozzle_temp == 220.5
    assert status.bed_temp == 60.0
    assert status.print_percentage == 45
    assert status.layer_num == 50
    print("PASSED")


def test_printer_status_to_dict():
    """Test PrinterStatus conversion to dictionary"""
    print("Test: PrinterStatus to dict...", end=" ")
    
    status = PrinterStatus(
        device_id="test123",
        nozzle_temp=220.0,
        bed_temp=60.0,
        print_percentage=75
    )
    
    data = status.to_dict()
    assert data["device_id"] == "test123"
    assert "temperatures" in data
    assert data["temperatures"]["nozzle"] == 220.0
    assert "progress" in data
    assert data["progress"]["percentage"] == 75
    print("PASSED")


def test_project_from_dict():
    """Test Project creation from dictionary"""
    print("Test: Project from dict...", end=" ")
    
    data = {
        "id": "proj123",
        "name": "Test Project",
        "created": "2024-01-01",
        "modified": "2024-01-02"
    }
    
    project = Project.from_dict(data)
    assert project.id == "proj123"
    assert project.name == "Test Project"
    print("PASSED")


def run_tests():
    """Run all model tests"""
    print("=" * 80)
    print("Testing Data Models")
    print("=" * 80)
    print()
    
    tests = [
        test_device_from_dict,
        test_device_to_dict,
        test_printer_status_from_mqtt,
        test_printer_status_to_dict,
        test_project_from_dict,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
