#!/usr/bin/env python3
"""
Test BambuClient HTTP API Client
=================================

Tests for the HTTP API client functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import BambuClient
from bambulab.client import BambuAPIError


def test_client_initialization():
    """Test client can be initialized"""
    print("Test: Client initialization...", end=" ")
    client = BambuClient("test_token")
    assert client.token == "test_token"
    assert client.BASE_URL == "https://api.bambulab.com"
    print("PASSED")


def test_headers_generation():
    """Test header generation"""
    print("Test: Header generation...", end=" ")
    client = BambuClient("test_token")
    headers = client._get_headers()
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Content-Type"] == "application/json"
    print("PASSED")


def test_endpoint_methods():
    """Test that endpoint methods exist"""
    print("Test: Endpoint methods exist...", end=" ")
    client = BambuClient("test_token")
    
    # Check methods exist
    assert hasattr(client, 'get_devices')
    assert hasattr(client, 'get_print_status')
    assert hasattr(client, 'get_user_profile')
    assert hasattr(client, 'get_projects')
    assert hasattr(client, 'create_project')
    print("PASSED")


def test_base_request_methods():
    """Test base HTTP methods exist"""
    print("Test: Base HTTP methods...", end=" ")
    client = BambuClient("test_token")
    
    assert hasattr(client, 'get')
    assert hasattr(client, 'post')
    assert hasattr(client, 'put')
    assert hasattr(client, 'delete')
    print("PASSED")


def run_tests():
    """Run all client tests"""
    print("=" * 80)
    print("Testing BambuClient")
    print("=" * 80)
    print()
    
    tests = [
        test_client_initialization,
        test_headers_generation,
        test_endpoint_methods,
        test_base_request_methods,
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
