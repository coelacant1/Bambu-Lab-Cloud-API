#!/usr/bin/env python3
"""
Test TokenManager and BambuAuthenticator
=========================================

Tests for token management and authentication.
"""

import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import TokenManager, BambuAuthenticator, BambuAuthError


def test_token_manager_init():
    """Test TokenManager initialization"""
    print("Test: TokenManager initialization...", end=" ")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"test_token": "real_token"}, f)
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        assert tm.count() == 1
        print("PASSED")
    finally:
        os.unlink(temp_file)


def test_add_token():
    """Test adding tokens"""
    print("Test: Add token...", end=" ")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("{}")
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        tm.add_token("custom1", "real1")
        assert tm.count() == 1
        assert tm.validate("custom1") == "real1"
        print("PASSED")
    finally:
        os.unlink(temp_file)


def test_validate_token():
    """Test token validation"""
    print("Test: Validate token...", end=" ")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"valid": "real_token", "another": "another_real"}, f)
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        assert tm.validate("valid") == "real_token"
        assert tm.validate("another") == "another_real"
        assert tm.validate("invalid") is None
        print("PASSED")
    finally:
        os.unlink(temp_file)


def test_remove_token():
    """Test removing tokens"""
    print("Test: Remove token...", end=" ")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"token1": "real1", "token2": "real2"}, f)
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        assert tm.count() == 2
        assert tm.remove_token("token1") == True
        assert tm.count() == 1
        assert tm.validate("token1") is None
        assert tm.validate("token2") == "real2"
        print("PASSED")
    finally:
        os.unlink(temp_file)


def test_list_tokens():
    """Test listing tokens"""
    print("Test: List tokens...", end=" ")
    
    long_token = "A" * 50
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"custom": long_token}, f)
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        tokens = tm.list_tokens()
        assert "custom" in tokens
        assert len(tokens["custom"]) < len(long_token)
        assert tokens["custom"].endswith("...")
        print("PASSED")
    finally:
        os.unlink(temp_file)


# BambuAuthenticator Tests

def test_authenticator_init_global():
    """Test BambuAuthenticator initialization with global region"""
    print("Test: Authenticator init (global)...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(region="global", token_file=temp_file)
        assert auth.base_url == "https://api.bambulab.com"
        assert auth.region == "global"
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_authenticator_init_china():
    """Test BambuAuthenticator initialization with China region"""
    print("Test: Authenticator init (china)...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(region="china", token_file=temp_file)
        assert auth.base_url == "https://api.bambulab.cn"
        assert auth.region == "china"
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_save_and_load_token():
    """Test token saving and loading"""
    print("Test: Save and load token...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(token_file=temp_file)
        
        test_token = "test_token_12345"
        auth.save_token(test_token)
        
        # Verify file was created
        assert os.path.exists(temp_file)
        
        # Load and verify token
        loaded_token = auth.load_token()
        assert loaded_token == test_token
        
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@patch('requests.Session.post')
def test_login_success(mock_post):
    """Test successful login without 2FA"""
    print("Test: Login success...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(token_file=temp_file)
        
        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true, "accessToken": "test_token_abc123"}'
        mock_response.json.return_value = {
            "success": True,
            "accessToken": "test_token_abc123"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        token = auth.login("test@example.com", "password")
        
        assert token == "test_token_abc123"
        # Verify token was saved
        loaded_token = auth.load_token()
        assert loaded_token == "test_token_abc123"
        
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@patch('requests.Session.get')
def test_verify_token_valid(mock_get):
    """Test token verification - valid token"""
    print("Test: Verify valid token...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(token_file=temp_file)
        
        # Mock successful API call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        is_valid = auth.verify_token("valid_token")
        assert is_valid == True
        
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@patch('requests.Session.get')
def test_verify_token_invalid(mock_get):
    """Test token verification - invalid token"""
    print("Test: Verify invalid token...", end=" ")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        auth = BambuAuthenticator(token_file=temp_file)
        
        # Mock failed API call
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        is_valid = auth.verify_token("invalid_token")
        assert is_valid == False
        
        print("PASSED")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_auth_error():
    """Test BambuAuthError exception"""
    print("Test: BambuAuthError...", end=" ")
    
    error = BambuAuthError("Test error message")
    assert str(error) == "Test error message"
    
    try:
        raise BambuAuthError("Test error")
    except BambuAuthError as e:
        assert "Test error" in str(e)
    
    print("PASSED")


def run_tests():
    """Run all auth tests"""
    print("=" * 80)
    print("Testing TokenManager and BambuAuthenticator")
    print("=" * 80)
    print()
    
    tests = [
        # TokenManager tests
        test_token_manager_init,
        test_add_token,
        test_validate_token,
        test_remove_token,
        test_list_tokens,
        # BambuAuthenticator tests
        test_authenticator_init_global,
        test_authenticator_init_china,
        test_save_and_load_token,
        test_login_success,
        test_verify_token_valid,
        test_verify_token_invalid,
        test_auth_error,
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
