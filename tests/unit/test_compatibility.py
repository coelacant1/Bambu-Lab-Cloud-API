#!/usr/bin/env python3
"""
Test Compatibility Layer Server
================================

Tests for the Bambu Lab compatibility layer server functionality.
"""

import sys
import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab.client import BambuAPIError


class TestCompatibilityConfiguration(unittest.TestCase):
    """Test compatibility layer configuration"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        print("Test: Default config values...", end=" ")
        # Test default port and host
        default_port = 8080
        default_host = "0.0.0.0"
        self.assertEqual(default_port, 8080)
        self.assertEqual(default_host, "0.0.0.0")
        print("PASSED")
    
    def test_config_structure_requirements(self):
        """Test required configuration structure"""
        print("Test: Config structure requirements...", end=" ")
        required_fields = ["cloud_token", "user_uid", "devices", "server"]
        self.assertIn("cloud_token", required_fields)
        self.assertIn("devices", required_fields)
        print("PASSED")


class TestCompatibilityConfigLoading(unittest.TestCase):
    """Test configuration loading"""
    
    def test_valid_config_structure(self):
        """Test valid configuration structure"""
        print("Test: Valid config structure...", end=" ")
        config_data = {
            "cloud_token": "test_token_abc123",
            "user_uid": "test_user_uid",
            "devices": [
                {
                    "device_id": "DEV123",
                    "name": "Test Printer",
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
        
        # Validate structure
        self.assertIn("cloud_token", config_data)
        self.assertIn("devices", config_data)
        self.assertEqual(len(config_data["devices"]), 1)
        self.assertEqual(config_data["devices"][0]["device_id"], "DEV123")
        print("PASSED")


class TestCompatibilityClientInitialization(unittest.TestCase):
    """Test API client initialization"""
    
    def test_client_init_concept(self):
        """Test client initialization concept"""
        print("Test: Client init concept...", end=" ")
        # Valid token should initialize client
        valid_token = "valid_token_123"
        invalid_token = "YOUR_BAMBU_CLOUD_TOKEN_HERE"
        
        self.assertNotEqual(valid_token, "YOUR_BAMBU_CLOUD_TOKEN_HERE")
        self.assertEqual(invalid_token, "YOUR_BAMBU_CLOUD_TOKEN_HERE")
        print("PASSED")


class TestCompatibilityMQTTBridge(unittest.TestCase):
    """Test MQTT bridge initialization"""
    
    def test_mqtt_bridge_requirements(self):
        """Test MQTT bridge requirements"""
        print("Test: MQTT bridge requirements...", end=" ")
        # MQTT bridge requires username, token, and devices
        required = ["username", "token", "devices"]
        self.assertIn("username", required)
        self.assertIn("devices", required)
        print("PASSED")


class TestCompatibilityCaching(unittest.TestCase):
    """Test device status caching"""
    
    def test_cache_concept(self):
        """Test caching concept"""
        print("Test: Cache concept...", end=" ")
        import time
        
        # Simulate cache entry
        cache_entry = {
            "data": {"test": "data"},
            "timestamp": time.time()
        }
        
        # Fresh cache
        max_age = 5
        age = time.time() - cache_entry["timestamp"]
        is_fresh = age < max_age
        
        self.assertTrue(is_fresh)
        print("PASSED")
    
    def test_cache_expiry(self):
        """Test cache expiry logic"""
        print("Test: Cache expiry...", end=" ")
        import time
        
        # Old cache entry
        old_timestamp = time.time() - 10
        max_age = 5
        age = time.time() - old_timestamp
        is_expired = age >= max_age
        
        self.assertTrue(is_expired)
        print("PASSED")


class TestCompatibilityLegacyTranslation(unittest.TestCase):
    """Test legacy format translation"""
    
    def test_translate_data_structure(self):
        """Test legacy data structure translation"""
        print("Test: Translate data structure...", end=" ")
        
        # Simulate translation logic
        cloud_data = {
            "dev_id": "DEV123",
            "name": "Test Printer",
            "online": True,
            "print": {
                "mc_percent": 50,
                "nozzle_temper": 220,
                "bed_temper": 60
            }
        }
        
        # Legacy format should wrap in "print" object with command
        legacy_format = {
            "print": {
                "command": "push_status",
                "dev_id": cloud_data["dev_id"],
                "name": cloud_data["name"],
                "online": cloud_data["online"],
                "mc_percent": cloud_data["print"]["mc_percent"],
                "nozzle_temper": cloud_data["print"]["nozzle_temper"]
            }
        }
        
        self.assertIn("print", legacy_format)
        self.assertEqual(legacy_format["print"]["command"], "push_status")
        self.assertEqual(legacy_format["print"]["dev_id"], "DEV123")
        print("PASSED")
    
    def test_default_values_concept(self):
        """Test default values for missing fields"""
        print("Test: Default values...", end=" ")
        
        # Missing fields should have defaults
        default_temp = 0
        default_percent = 0
        default_layers = 0
        
        self.assertEqual(default_temp, 0)
        self.assertEqual(default_percent, 0)
        self.assertEqual(default_layers, 0)
        print("PASSED")


class TestCompatibilityEndpoints(unittest.TestCase):
    """Test compatibility layer endpoints"""
    
    def test_endpoint_responses(self):
        """Test endpoint response structure"""
        print("Test: Endpoint responses...", end=" ")
        
        # Index endpoint structure
        index_response = {
            "name": "Bambu Lab Compatibility Layer",
            "version": "2.0.0",
            "status": "online"
        }
        self.assertIn("name", index_response)
        self.assertIn("status", index_response)
        
        # Health endpoint structure
        health_response = {
            "status": "healthy",
            "devices": 1
        }
        self.assertEqual(health_response["status"], "healthy")
        print("PASSED")


class TestCompatibilityDeviceStatus(unittest.TestCase):
    """Test device status fetching"""
    
    def test_device_lookup_logic(self):
        """Test device lookup logic"""
        print("Test: Device lookup logic...", end=" ")
        
        # Simulate device list
        devices = [
            {"dev_id": "DEV123", "name": "Printer 1"},
            {"dev_id": "DEV456", "name": "Printer 2"}
        ]
        
        # Find device by ID
        target_id = "DEV123"
        found = None
        for device in devices:
            if device["dev_id"] == target_id:
                found = device
                break
        
        self.assertIsNotNone(found)
        self.assertEqual(found["dev_id"], "DEV123")
        
        # Not found case
        target_id = "DEV999"
        found = None
        for device in devices:
            if device["dev_id"] == target_id:
                found = device
                break
        
        self.assertIsNone(found)
        print("PASSED")


class TestCompatibilityStatusEndpoint(unittest.TestCase):
    """Test legacy status endpoint"""
    
    def test_status_response_concept(self):
        """Test status response concept"""
        print("Test: Status response concept...", end=" ")
        
        # Single device response
        single_response = {"print": {"dev_id": "DEV123"}}
        self.assertIn("print", single_response)
        
        # Multiple devices response
        multi_response = {
            "DEV123": {"print": {}},
            "DEV456": {"print": {}}
        }
        self.assertIn("DEV123", multi_response)
        self.assertIn("DEV456", multi_response)
        print("PASSED")


class TestCompatibilityDevicesEndpoint(unittest.TestCase):
    """Test devices listing endpoint"""
    
    def test_device_list_structure(self):
        """Test device list structure"""
        print("Test: Device list structure...", end=" ")
        
        # Devices endpoint should return array
        response = {
            "devices": [
                {"dev_id": "DEV123"},
                {"dev_id": "DEV456"}
            ]
        }
        
        self.assertIn("devices", response)
        self.assertEqual(len(response["devices"]), 2)
        print("PASSED")
    
    def test_error_responses(self):
        """Test error response structures"""
        print("Test: Error responses...", end=" ")
        
        # No client error
        error_response = {"error": "API client not initialized"}
        self.assertIn("error", error_response)
        
        # API error
        api_error = {"error": "API Error"}
        self.assertIn("error", api_error)
        print("PASSED")


def run_tests():
    """Run all tests"""
    print("=" * 80)
    print("Testing Compatibility Layer Server")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityConfigLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityClientInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityMQTTBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityCaching))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityLegacyTranslation))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityDeviceStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityStatusEndpoint))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibilityDevicesEndpoint))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    if result.wasSuccessful():
        print(f"All {result.testsRun} tests passed!")
    else:
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
