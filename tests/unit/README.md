# Unit Tests

Automated unit tests for individual components. These tests use mocking and don't require real API credentials.

## Running Tests

Run all unit tests:
```bash
python -m unittest discover tests/unit
```

Run individual test files:
```bash
python -m unittest tests/unit/test_client.py
python -m unittest tests/unit/test_models.py
python -m unittest tests/unit/test_mqtt_commands.py
python -m unittest tests/unit/test_auth.py
```

## Test Files

- **`test_auth.py`** - Authentication and token management
- **`test_client.py`** - HTTP API client methods
- **`test_models.py`** - Data model classes (Device, PrinterStatus, etc.)
- **`test_mqtt_commands.py`** - MQTT control commands with mocked connections
- **`test_compatibility.py`** - Compatibility tests
- **`test_proxy.py`** - Proxy server functionality

## No Credentials Required

These tests are fully mocked and don't make real API calls. They're designed to:
- Run in CI/CD pipelines
- Verify code changes don't break existing functionality
- Test edge cases and error handling
- Validate data parsing and formatting
