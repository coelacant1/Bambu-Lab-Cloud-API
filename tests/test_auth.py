#!/usr/bin/env python3
"""
Test TokenManager Authentication
=================================

Tests for token management and authentication.
"""

import sys
import os
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import TokenManager


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
    """Test listing tokens (masked)"""
    print("Test: List tokens (masked)...", end=" ")
    
    long_token = "A" * 50
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"custom": long_token}, f)
        temp_file = f.name
    
    try:
        tm = TokenManager(temp_file)
        tokens = tm.list_tokens()
        assert "custom" in tokens
        assert len(tokens["custom"]) < len(long_token)  # Should be masked
        assert tokens["custom"].endswith("...")
        print("PASSED")
    finally:
        os.unlink(temp_file)


def run_tests():
    """Run all auth tests"""
    print("=" * 80)
    print("Testing TokenManager")
    print("=" * 80)
    print()
    
    tests = [
        test_token_manager_init,
        test_add_token,
        test_validate_token,
        test_remove_token,
        test_list_tokens,
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
