# Bambu Lab Cloud API Tests

## Overview

This directory contains comprehensive test suites for the Bambu Lab Cloud API library. The tests are organized into three categories:

- **`unit/`** - Unit tests for API methods, models, and local functionality (mocked, no real API calls)
- **`integration/`** - Integration tests that verify imports and object instantiation (no credentials needed)
- **`manual/`** - Live tests against the actual Bambu Lab Cloud API (requires credentials)

## Directory Structure

### `unit/` - Unit Tests

Automated tests that use mocking and don't require real API credentials. These tests verify individual components work correctly in isolation.

**Files:**
- `test_auth.py` - Authentication and token management tests
- `test_client.py` - HTTP API client methods tests
- `test_models.py` - Data model classes (Device, PrinterStatus, etc.)
- `test_mqtt_commands.py` - MQTT control commands with mocked connections
- `test_compatibility.py` - Compatibility tests
- `test_proxy.py` - Proxy server functionality tests

**Run unit tests:**
```bash
python -m unittest discover tests/unit
```

### `integration/` - Integration Tests

Tests that verify the library components work together correctly without requiring live API credentials. These test imports, object instantiation, and basic functionality.

**Files:**
- `test_integration.py` - Module imports and basic functionality tests

**Run integration tests:**
```bash
python tests/integration/test_integration.py
```

### `manual/` - Manual/Live Tests

Interactive tests that exercise the actual Bambu Lab Cloud API. These require valid credentials and an active printer connection.

**Files:**
- `test_comprehensive.py` - Full API and MQTT test suite
- `test_proxy_server.py` - Proxy server endpoint tests
- `test_config.json.example` - Configuration template

**Configuration:**
```bash
cd tests/manual
cp test_config.json.example test_config.json
nano test_config.json  # Add your Bambu Cloud token
```

**Run manual tests:**
```bash
python tests/manual/test_comprehensive.py
python tests/manual/test_proxy_server.py
```

## Running All Tests

### Run All Unit Tests
```bash
python -m unittest discover tests/unit
```

### Run Integration Tests (No Credentials Needed)
```bash
python tests/integration/test_integration.py
```

### Run Comprehensive Live Tests
```bash
# Setup credentials first
cd tests/manual
cp test_config.json.example test_config.json
nano test_config.json

# Run tests
python test_comprehensive.py
```

### Run Individual Unit Tests
```bash
python -m unittest tests/unit/test_client.py
python -m unittest tests/unit/test_mqtt_commands.py
python -m unittest tests/unit/test_models.py
```

## Configuration

### `manual/test_config.json`
Main configuration file for live tests. Copy from `test_config.json.example` in the `manual/` directory:

```json
{
  "cloud_token": "YOUR_BAMBU_CLOUD_TOKEN",
  "test_modes": {
    "cloud_api": true,
    "mqtt": true,
    "video_stream": true,
    "file_upload": false,
    "local_ftp": false
  },
  "timeouts": {
    "mqtt_connect": 10,
    "video_frame": 15,
    "api_request": 30
  }
}
```

**Getting Your Cloud Token:**
1. Log into Bambu Studio/Handy
2. Go to Settings -> Account
3. Copy your access token

## Test Categories Explained

### Unit Tests (`unit/`)
- **Purpose:** Test individual components in isolation
- **Credentials Required:** No
- **Mocking:** Yes
- **When to Run:** During development, before commits, in CI/CD
- **Examples:** Testing that API methods format requests correctly, models parse data correctly

### Integration Tests (`integration/`)
- **Purpose:** Test that components work together
- **Credentials Required:** No
- **Mocking:** No (but no real API calls)
- **When to Run:** To verify imports and basic instantiation work
- **Examples:** Testing that all modules can be imported, objects can be created

### Manual/Live Tests (`manual/`)
- **Purpose:** Test against real Bambu Lab Cloud API
- **Credentials Required:** Yes
- **Mocking:** No
- **When to Run:** Manual testing, verification of new features
- **Examples:** Testing actual API responses, MQTT connections, video streams

## Running Tests

### Quick Start

**Run all automated tests (no credentials needed):**
```bash
# From repository root
python -m unittest discover tests/unit
python tests/integration/test_integration.py
```

**Run live API tests (credentials required):**
```bash
cd tests/manual
cp test_config.json.example test_config.json
nano test_config.json  # Add your token
python test_comprehensive.py
```

### Run All Comprehensive Tests
```bash
python test_comprehensive.py
```

### Run Integration Tests (No Credentials Needed)
```bash
python test_integration.py
```

### Run Unit Tests
```bash
python -m unittest test_client.py
python -m unittest test_mqtt_commands.py
python -m unittest test_models.py
```

### Run All Unit Tests
```bash
python -m unittest discover
```

## Test Modes

You can enable/disable different test sections in `test_config.json`:

- **cloud_api**: Tests Cloud API endpoints (device info, status, profile)
- **mqtt**: Tests MQTT connection and data streaming
- **video_stream**: Tests video streaming (RTSP/JPEG)
- **file_upload**: Tests file upload to cloud (disabled by default - creates real files!)
- **local_ftp**: Tests local FTP upload (requires local network access)

## Privacy Warning

The comprehensive test output displays sensitive information:
- Device serial numbers
- Access codes  
- User IDs and emails
- Authentication tokens (TTCode)

Do not share test output publicly without redacting sensitive data.

## Expected Behavior

### If Printer is Online
- All tests should pass
- MQTT will receive live data
- Temperature, fan, and progress data will be displayed
- Video stream tests may capture frames

### If Printer is Offline
- Cloud API tests will pass (returns cached data)
- MQTT will connect but receive no data (expected)
- Video stream tests will fail (expected)

### If No Printer Bound
- Device-related tests will be skipped
- User profile and account tests will still pass
- Module import and structure tests will pass

## Continuous Integration

These tests can be run in CI/CD with mocked credentials for basic validation. For full integration testing, real credentials are required but should be stored as secrets.

## Contributing

When adding new API methods or features:
1. Add corresponding tests
2. Update `test_comprehensive.py` to print all new data fields
3. Update `TEST_OUTPUT_GUIDE.md` with descriptions of new output
4. Ensure tests pass with and without live credentials

## Troubleshooting

**"Configuration needed" error**
- Copy `test_config.json.example` to `test_config.json`
- Add your Bambu Cloud token

**MQTT connection timeout**
- Check your token is valid
- Ensure firewall allows MQTT connections
- Verify printer is online

**Video stream fails**
- Printer must be on local network
- Access code must be correct
- RTSP ports (X1) or HTTP (P1/A1) must be accessible

**API errors (401, 403)**
- Token expired - get a new one from Bambu Studio
- Account doesn't have access to requested resources

## More Information

- [Test Output Guide](TEST_OUTPUT_GUIDE.md) - Complete list of all data printed
- [Main README](../README.md) - Library documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

