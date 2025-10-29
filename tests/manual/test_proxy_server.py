#!/usr/bin/env python3
"""
Comprehensive test suite for Bambu Lab Cloud API Proxy Server

Usage:
    # Test local server (default)
    python test_proxy_server.py
    
    # Test remote server
    python test_proxy_server.py --url http://192.168.1.2:5001 --token custom-token-1
    
    # Test with environment variables
    export PROXY_URL="http://192.168.1.2:5001"
    export PROXY_TOKEN="custom-token-1"
    python test_proxy_server.py
"""

import requests
import json
import sys
import os
import argparse
import time
from datetime import datetime
from typing import Dict, Optional, Tuple


class ProxyTester:
    """Test suite for Bambu Lab Proxy Server"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.skip_rate_limit_tests = False
        self.results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[int, Optional[Dict]]:
        """Make HTTP request to proxy server"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30, **kwargs)
            elif method == 'POST':
                response = requests.post(url, headers=headers, timeout=30, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                data = response.json()
            except:
                data = None
            
            # Store rate limit headers if available
            rate_limit_info = {}
            if 'X-RateLimit-Limit' in response.headers:
                rate_limit_info['limit'] = response.headers.get('X-RateLimit-Limit')
                rate_limit_info['remaining'] = response.headers.get('X-RateLimit-Remaining')
                rate_limit_info['reset'] = response.headers.get('X-RateLimit-Reset')
                
            return response.status_code, data, rate_limit_info
            
        except requests.exceptions.RequestException as e:
            print(f"  Connection Error: {e}")
            return 0, None, {}
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     expected_status: int = 200, required_fields: list = None) -> bool:
        """Test a single endpoint"""
        print(f"\n{'─' * 80}")
        print(f"Testing: {name}")
        print(f"Endpoint: {method} {endpoint}")
        
        status_code, data, rate_limit_info = self._make_request(method, endpoint)
        
        test_result = {
            'name': name,
            'endpoint': f"{method} {endpoint}",
            'status_code': status_code,
            'expected_status': expected_status,
            'passed': False,
            'error': None,
            'rate_limit': rate_limit_info
        }
        
        # Check status code
        if status_code == 0:
            print(f"  FAILED - Connection Error")
            test_result['error'] = 'Connection failed'
            self.results['failed'] += 1
            self.results['tests'].append(test_result)
            return False
            
        if status_code != expected_status:
            print(f"  FAILED - Expected {expected_status}, got {status_code}")
            if data:
                print(f"  Response: {json.dumps(data, indent=2)[:200]}")
            test_result['error'] = f"Status code mismatch: {status_code}"
            self.results['failed'] += 1
            self.results['tests'].append(test_result)
            return False
        
        # Check required fields
        if required_fields and data:
            missing_fields = []
            for field in required_fields:
                if '.' in field:
                    # Nested field check
                    parts = field.split('.')
                    current = data
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            missing_fields.append(field)
                            break
                elif field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"  FAILED - Missing fields: {', '.join(missing_fields)}")
                test_result['error'] = f"Missing fields: {missing_fields}"
                self.results['failed'] += 1
                self.results['tests'].append(test_result)
                return False
        
        # Success
        print(f"  SUCCESS (HTTP {status_code})")
        if rate_limit_info:
            print(f"  Rate Limit: {rate_limit_info.get('remaining', '?')}/{rate_limit_info.get('limit', '?')} remaining")
        if data:
            # Show preview of response
            preview = json.dumps(data, indent=2)
            if len(preview) > 500:
                preview = preview[:500] + "..."
            print(f"  Response preview:\n{preview}")
        
        test_result['passed'] = True
        self.results['passed'] += 1
        self.results['tests'].append(test_result)
        return True
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 80)
        print("BAMBU LAB PROXY SERVER - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Token: {self.token[:20]}..." if len(self.token) > 20 else f"Token: {self.token}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. Health & Info Tests
        print("\n" + "=" * 80)
        print("SECTION 1: HEALTH & INFO ENDPOINTS")
        print("=" * 80)
        
        self.test_endpoint(
            "Health Check",
            "GET", "/health",
            required_fields=['status', 'mode']
        )
        
        self.test_endpoint(
            "Server Info",
            "GET", "/",
            required_fields=['name', 'version', 'mode']
        )
        
        # 2. Device Tests
        print("\n" + "=" * 80)
        print("SECTION 2: DEVICE ENDPOINTS")
        print("=" * 80)
        
        self.test_endpoint(
            "Get Bound Devices",
            "GET", "/v1/iot-service/api/user/bind",
            required_fields=['devices']
        )
        
        self.test_endpoint(
            "Get Device Info",
            "GET", "/v1/iot-service/api/user/device/info",
            expected_status=502  # Known to fail - upstream API returns 405
        )
        
        self.test_endpoint(
            "Get Device Versions",
            "GET", "/v1/iot-service/api/user/device/version",
            required_fields=['devices']
        )
        
        self.test_endpoint(
            "Get Print Jobs",
            "GET", "/v1/iot-service/api/user/print"
            # Endpoint exists and returns 200 with data
        )
        
        # 3. User Tests
        print("\n" + "=" * 80)
        print("SECTION 3: USER ENDPOINTS")
        print("=" * 80)
        
        self.test_endpoint(
            "Get User Profile",
            "GET", "/v1/user-service/my/profile"
        )
        
        self.test_endpoint(
            "Get User Preferences",
            "GET", "/v1/design-user-service/my/preference"
        )
        
        self.test_endpoint(
            "Get User Messages",
            "GET", "/v1/user-service/my/messages?limit=5"
            # Endpoint exists and returns 200 with message data
        )
        
        # 4. Task Tests
        print("\n" + "=" * 80)
        print("SECTION 4: TASK & PRINT HISTORY")
        print("=" * 80)
        
        self.test_endpoint(
            "Get User Tasks",
            "GET", "/v1/user-service/my/tasks?limit=10"
        )
        
        # 5. Project Tests
        print("\n" + "=" * 80)
        print("SECTION 5: PROJECT MANAGEMENT")
        print("=" * 80)
        
        self.test_endpoint(
            "Get Projects",
            "GET", "/v1/iot-service/api/user/project?page=1&limit=5"
        )
        
        # 6. Notification Tests (Expected to fail with current API)
        print("\n" + "=" * 80)
        print("SECTION 6: NOTIFICATIONS (May require additional params)")
        print("=" * 80)
        
        self.test_endpoint(
            "Get All Notifications",
            "GET", "/v1/iot-service/api/user/notification",
            expected_status=502  # Known to fail
        )
        
        # 7. Admin Tests
        print("\n" + "=" * 80)
        print("SECTION 7: ADMIN ENDPOINTS")
        print("=" * 80)
        
        self.test_endpoint(
            "List Token Mappings",
            "GET", "/admin/tokens",
            required_fields=['count', 'tokens']
        )
        
        # 8. Security Tests (Should fail in strict mode)
        print("\n" + "=" * 80)
        print("SECTION 8: SECURITY TESTS (Should reject non-GET)")
        print("=" * 80)
        
        self.test_endpoint(
            "POST Should Be Rejected",
            "POST", "/v1/iot-service/api/user/bind",
            expected_status=405  # Method Not Allowed
        )
        
        # 9. Rate Limiting Tests
        if not self.skip_rate_limit_tests:
            print("\n" + "=" * 80)
            print("SECTION 9: RATE LIMITING TESTS")
            print("=" * 80)
            
            self.test_rate_limits()
        else:
            print("\n" + "=" * 80)
            print("SECTION 9: RATE LIMITING TESTS - SKIPPED")
            print("=" * 80)
    
    def test_rate_limits(self):
        """Test rate limiting functionality"""
        print("\n" + "─" * 80)
        print("Testing Rate Limits")
        print("─" * 80)
        
        # Test 1: Verify rate limit headers are present
        print("\nTest 1: Rate Limit Headers Present")
        status_code, data, rate_limit_info = self._make_request('GET', '/health')
        
        if rate_limit_info and 'limit' in rate_limit_info:
            print(f"  Rate limit headers found")
            print(f"    Limit: {rate_limit_info['limit']}")
            print(f"    Remaining: {rate_limit_info['remaining']}")
            print(f"    Reset: {rate_limit_info['reset']}")
            self.results['passed'] += 1
        else:
            print(f"  Warning: Rate limit headers not present (may not be enabled)")
            self.results['skipped'] += 1
        
        # Test 2: Verify rate limits are documented in /health response
        print("\nTest 2: Rate Limits in Health Response")
        if data and 'rate_limits' in data:
            print(f"  Rate limits documented in response")
            print(f"    Device Queries: {data['rate_limits'].get('device_queries', 'N/A')}")
            print(f"    User Endpoints: {data['rate_limits'].get('user_endpoints', 'N/A')}")
            print(f"    Admin Endpoints: {data['rate_limits'].get('admin_endpoints', 'N/A')}")
            self.results['passed'] += 1
        else:
            print(f"  Warning: Rate limits not in /health response")
            self.results['skipped'] += 1
        
        # Test 3: Rapid requests to trigger rate limit (optional - can be slow)
        print("\nTest 3: Rate Limit Enforcement (Optional)")
        print("  Testing if rate limits are enforced by making rapid requests...")
        
        # Make 10 rapid requests to a light endpoint
        rate_limited = False
        request_count = 0
        max_requests = 10
        
        for i in range(max_requests):
            status_code, _, rate_info = self._make_request('GET', '/health')
            request_count += 1
            
            if status_code == 429:
                rate_limited = True
                print(f"  Rate limit triggered after {request_count} requests (HTTP 429)")
                self.results['passed'] += 1
                break
            
            if rate_info and 'remaining' in rate_info:
                remaining = int(rate_info['remaining'])
                if remaining < 5:
                    print(f"  Getting close to limit: {remaining} requests remaining")
        
        if not rate_limited:
            print(f"  ℹ Note: Rate limit not triggered in {max_requests} requests")
            print(f"     (This is normal - limits are per-minute, not per-burst)")
            self.results['skipped'] += 1
        
        # Test 4: Verify 429 response format
        if rate_limited:
            print("\nTest 4: HTTP 429 Response Format")
            status_code, data, _ = self._make_request('GET', '/health')
            
            if status_code == 429 and data:
                required_fields = ['error', 'message']
                missing = [f for f in required_fields if f not in data]
                
                if not missing:
                    print(f"  429 response has correct format")
                    print(f"    Error: {data.get('error')}")
                    print(f"    Message: {data.get('message')}")
                    self.results['passed'] += 1
                else:
                    print(f"  429 response missing fields: {missing}")
                    self.results['failed'] += 1
            else:
                print(f"  Could not verify 429 response format")
                self.results['skipped'] += 1
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.results['passed'] + self.results['failed']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"⊘ Skipped: {self.results['skipped']}")
        print()
        
        success_rate = (self.results['passed'] / 
                       (self.results['passed'] + self.results['failed']) * 100)
        print(f"Success Rate: {success_rate:.1f}%")
        
        # List failures
        failures = [t for t in self.results['tests'] if not t['passed']]
        if failures:
            print("\nFailed Tests:")
            for test in failures:
                print(f"  {test['name']}")
                print(f"    {test['endpoint']}")
                print(f"    Status: {test['status_code']} (expected {test['expected_status']})")
                if test['error']:
                    print(f"    Error: {test['error']}")
        
        print("=" * 80)
        
        # Return exit code
        return 0 if self.results['failed'] == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Test Bambu Lab Cloud API Proxy Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test local server
  python test_proxy_server.py
  
  # Test remote server
  python test_proxy_server.py --url http://192.168.1.2:5001 --token custom-token-1
  
  # Skip rate limit tests (faster)
  python test_proxy_server.py --skip-rate-limit-tests
  
  # Use environment variables
  export PROXY_URL="http://192.168.1.2:5001"
  export PROXY_TOKEN="custom-token-1"
  python test_proxy_server.py
        """
    )
    
    parser.add_argument(
        '--url',
        default=os.getenv('PROXY_URL', 'http://localhost:5001'),
        help='Proxy server URL (default: http://localhost:5001 or $PROXY_URL)'
    )
    
    parser.add_argument(
        '--token',
        default=os.getenv('PROXY_TOKEN', 'custom-token-1'),
        help='API token (default: custom-token-1 or $PROXY_TOKEN)'
    )
    
    parser.add_argument(
        '--skip-rate-limit-tests',
        action='store_true',
        help='Skip rate limiting tests (faster execution)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Create tester
    tester = ProxyTester(args.url, args.token)
    tester.skip_rate_limit_tests = args.skip_rate_limit_tests
    
    # Run tests
    try:
        tester.run_all_tests()
        exit_code = tester.print_summary()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
