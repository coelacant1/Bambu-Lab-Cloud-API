# Integration Tests

Tests that verify library components work together correctly without requiring live API credentials.

## Running Tests

```bash
python tests/integration/test_integration.py
```

## Test Files

- **`test_integration.py`** - Module imports and basic functionality

## What These Tests Verify

- All modules can be imported successfully
- Objects can be instantiated
- Methods exist and have correct signatures
- Basic functionality works without API calls

## No Credentials Required

These tests don't make real API calls and are safe to run without configuration.
