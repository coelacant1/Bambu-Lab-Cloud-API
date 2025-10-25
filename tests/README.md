# Bambu Lab Cloud API Tests

## Overview

This directory contains comprehensive test suites for the Bambu Lab Cloud API library. The tests are designed to validate functionality and provide detailed output of all API responses.

## Test Files

### `test_comprehensive.py` - Enhanced with Full Data Output
The main comprehensive test suite that exercises all major functionality:

**Features:**
- Detailed Data Output: Prints ALL data fields from API responses
- Live MQTT Monitoring: Shows real-time data streams
- Temperature Tracking: Displays nozzle, bed, and chamber temperatures
- Fan Speed Monitoring: Shows all fan speeds
- Complete Field Lists: Dumps every field returned by the API
- Control Command Testing: Validates all MQTT control methods
- Video Stream Testing: Tests camera access and video frames

**What Gets Printed:**
- Device info (name, serial, model, status, ALL fields)
- Firmware versions (current, available, OTA data, AMS versions)
- Print status (temperatures, fans, progress, ALL fields)
- User profile (UID, name, email, printer models, ALL fields)
- Camera credentials (TTCode, password, auth key, ALL fields)
- Projects, tasks, notifications, messages (with full details)
- Slicer settings and resources
- MQTT data streams (print data, AMS data, camera, lights)
- MQTT control commands (pause, resume, stop, temp controls)

**Usage:**
```bash
# Configure credentials
cp test_config.json.example test_config.json
nano test_config.json  # Add your Bambu Cloud token

# Run tests
python test_comprehensive.py
```

**Output Example:**
```
======================================================================
  Cloud API Tests
======================================================================

    DEVICE INFO:
       Name: X1 Carbon
       Serial: 01S00A123456789
       Model: X1 Carbon (3DP01)
       Online: Yes
       ...

    ALL DEVICE DATA FIELDS (25 fields):
       dev_id: 01S00A123456789
       name: X1 Carbon
       online: True
       ...

    FIRMWARE VERSION DATA:
       Firmware: 1.07.00.00
       ...
```

See [TEST_OUTPUT_GUIDE.md](TEST_OUTPUT_GUIDE.md) for complete details on all output.

### `test_integration.py`
Tests module imports and basic functionality without requiring credentials.

### `test_client.py`
Unit tests for the BambuClient HTTP API methods.

### `test_mqtt_commands.py`
Unit tests for MQTT control commands with mocked connections.

### `test_auth.py`
Tests for authentication and token management.

### `test_models.py`
Tests for data model classes (Device, PrinterStatus, etc.).

### `test_proxy.py`
Tests for the proxy server functionality.

## Configuration

### `test_config.json`
Main configuration file for live tests. Copy from `test_config.json.example`:

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
2. Go to Settings → Account
3. Copy your access token

## Running Tests

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

