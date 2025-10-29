# Manual/Live Tests

Interactive tests that exercise the actual Bambu Lab Cloud API. These require valid credentials and test against real printers.

## Setup

1. Copy the configuration template:
```bash
cp test_config.json.example test_config.json
```

2. Edit `test_config.json` and add your Bambu Cloud token:
```json
{
  "cloud_token": "YOUR_BAMBU_CLOUD_TOKEN",
  "test_modes": {
    "cloud_api": true,
    "mqtt": true,
    "video_stream": true,
    "file_upload": false,
    "local_ftp": false
  }
}
```

3. Get your token from Bambu Studio/Handy:
   - Open Bambu Studio or Bambu Handy
   - Go to Settings → Account
   - Copy your access token

## Running Tests

**Comprehensive test suite:**
```bash
python test_comprehensive.py
```

**Proxy server tests:**
```bash
python test_proxy_server.py
```

**Test remote proxy server:**
```bash
python test_proxy_server.py --url http://server:5001 --token your-token
```

## Test Files

- **`test_comprehensive.py`** - Full API and MQTT test suite with detailed output
- **`test_proxy_server.py`** - Tests for read-only proxy server endpoints
- **`test_config.json.example`** - Configuration template

## What These Tests Do

### test_comprehensive.py
- Tests all Cloud API endpoints (devices, status, profile, projects)
- Connects to MQTT and displays live printer data
- Tests video streaming (RTSP/JPEG)
- Tests file uploads (optional)
- Tests local FTP (optional)
- Displays ALL data fields from API responses

### test_proxy_server.py
- Tests proxy server endpoints
- Validates GET requests
- Verifies POST rejection in strict mode
- Tests pagination and filtering

## Privacy Warning

**These tests display sensitive information:**
- Device serial numbers
- Access codes
- User IDs and emails
- Authentication tokens

**Do not share test output publicly without redacting sensitive data.**

## Expected Behavior

### Printer Online
- All tests pass
- MQTT receives live data
- Temperature, fan, and progress data displayed
- Video stream tests may capture frames

### Printer Offline
- Cloud API tests pass (returns cached data)
- MQTT connects but receives no data (expected)
- Video stream tests fail (expected)

### No Printer Bound
- Device tests skipped
- User profile tests pass
- Module tests pass

## Test Modes

Configure in `test_config.json`:

- **cloud_api:** Test Cloud API endpoints
- **mqtt:** Test MQTT connection and streaming
- **video_stream:** Test video streaming
- **file_upload:** Test file uploads (creates real files!)
- **local_ftp:** Test local FTP (requires local network access)
