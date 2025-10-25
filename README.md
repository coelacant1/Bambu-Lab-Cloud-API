# Bambu Lab Cloud API Python Library Implementation

**Documentation and tools for the Bambu Lab Cloud API based on network traffic analysis**

[![Publish to PyPI](https://github.com/coelacant1/Bambu-Lab-Cloud-API/actions/workflows/publish.yml/badge.svg)](https://github.com/coelacant1/Bambu-Lab-Cloud-API/actions/workflows/publish.yml)
[![Tests](https://github.com/coelacant1/Bambu-Lab-Cloud-API/actions/workflows/tests.yml/badge.svg)](https://github.com/coelacant1/Bambu-Lab-Cloud-API/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-AGPL--v3-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()

Documentation and tooling for communicating with Bambu Lab 3D printers via their Cloud API, MQTT protocol, and local connections.

My goal with this project was to create a proxy for handling read only data from my printer farm, but decided to expand it into a more complete library. I won't be targetting all of the functionality for testing, as I will primarily focus on read operations. 

## Features

- **API Documentation** - Complete endpoint reference with examples
- **Python Library** - Unified client for Cloud API, MQTT, local FTP, and video streams
- **Authentication** - Multiple methods to obtain access tokens
- **MQTT Support** - Real-time printer monitoring and control
- **File Upload** - Cloud API and local FTP upload support
- **Video Streaming** - RTSP (X1 series) and JPEG frame streaming (A1/P1 series)
- **Compatibility Layer** - Restore legacy local API without developer mode
- **Proxy Servers** - Safe API gateways (strict read-only and full modes)
- **Testing Suite** - Comprehensive unit tests for all functionality
- **G-code Reference** - Command documentation for printer models

![P1S Video Stream](screenshots/P1SStream.png)
*Live JPEG frame streaming from P1S printer camera*

## Quick Test (Auto Unit Test)

Test the library with your printer:

```bash
cd tests
cp test_config.json.example test_config.json
# Edit test_config.json with your token
python3 test_comprehensive.py
```

The test suite:
- Connects to Bambu Cloud
- Tests all API endpoints
- Validates MQTT connectivity
- Tests real-time monitoring
- Verifies library functionality

> You can pull your auth code via proxy.py in servers/



## Documentation

### Modular API Documentation

Complete API documentation split into focused modules:

- **[API_INDEX.md](API_INDEX.md)** - Master index and quick start guide
- **[API_AUTHENTICATION.md](API_AUTHENTICATION.md)** - Authentication methods and security
- **[API_DEVICES.md](API_DEVICES.md)** - Device management and print jobs
- **[API_USERS.md](API_USERS.md)** - User profiles and accounts
- **[API_FILES_PRINTING.md](API_FILES_PRINTING.md)** - Cloud file upload and printing
- **[API_MQTT.md](API_MQTT.md)** - Real-time MQTT protocol
- **[API_AMS_FILAMENT.md](API_AMS_FILAMENT.md)** - AMS and filament data
- **[API_CAMERA.md](API_CAMERA.md)** - Camera and video streaming
- **[API_REFERENCE.md](API_REFERENCE.md)** - Error codes and conventions


## Python Library

The `bambulab/` package provides a unified Python interface for Bambu Lab Cloud API access.

### Installation

```bash
# Install from PyPI
pip install bambu-lab-cloud-api

# Or install directly from GitHub
pip install git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git

# With server components
pip install bambu-lab-cloud-api[server]
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Cloud API

```python
from bambulab import BambuClient

client = BambuClient(token="your_token")
devices = client.get_devices()
for device in devices:
    print(f"{device['name']}: {device['print_status']}")

# Upload file to cloud
result = client.upload_file("model.3mf")
print(f"Uploaded: {result['file_url']}")
```

### MQTT Monitoring

```python
from bambulab import MQTTClient

def on_message(device_id, data):
    print(f"Progress: {data['print']['mc_percent']}%")

mqtt = MQTTClient("uid", "token", "device_serial", on_message=on_message)
mqtt.connect(blocking=True)
```

### Local File Upload (FTP)

```python
from bambulab import LocalFTPClient

client = LocalFTPClient("192.168.1.100", "access_code")
client.connect()
result = client.upload_file("model.3mf")
client.disconnect()
print(f"Uploaded to: {result['remote_path']}")
```

### Video Streaming

```python
from bambulab import JPEGFrameStream, RTSPStream

# For A1/P1 series (JPEG frames)
with JPEGFrameStream("192.168.1.100", "access_code") as stream:
    frame = stream.get_frame()
    with open('snapshot.jpg', 'wb') as f:
        f.write(frame)

# For X1 series (RTSP)
stream = RTSPStream("192.168.1.100", "access_code")
url = stream.get_stream_url()  # Use with VLC, ffmpeg
```

See [bambulab/README.md](bambulab/README.md) for complete library documentation.

## Servers

### Compatibility Layer (`servers/compatibility.py`)

Restores legacy local API functionality without developer mode. Bridges Home Assistant, Octoprint, and other tools to the Cloud API.

```bash
cd servers
cp compatibility_config.json.example compatibility_config.json
# Edit with your credentials
python3 compatibility.py
```

Features:
- Mimics legacy local API endpoints
- Works without developer mode
- Real-time MQTT bridge
- Multi-device support
- Port 8080 by default

> This requires additional testing, I only lightly tested this.

### Proxy Server (`servers/proxy.py`)

API gateway with two modes for different security requirements:

**Strict Mode (port 5001)** - Read-only, maximum safety:
```bash
python3 proxy.py strict
```

**Full Mode (port 5003)** - Complete 1:1 proxy:
```bash
python3 proxy.py full
```

Features:
- Custom token authentication
- Request filtering by mode
- Health monitoring endpoints

## CLI Tools

Located in `cli_tools/` directory:

| Script | Purpose |
|--------|---------|
| `query.py` | Query printer information and status |
| `monitor.py` | Real-time MQTT monitoring |

See [cli_tools/README.md](cli_tools/README.md) for usage details.

## API Endpoints

### Verified Working (Read Operations)

- Get Bound Devices
- Get Device Version/Firmware
- Get Print Status
- Get Projects
- Get User Profile
- Get User Tasks/History
- Get User Messages
- Get User Preferences
- Get Slicer Resources

### Partially Tested (Write Operations)

- User Login
- Get TTCode (Webcam Access)
- Update Device Info
- File Upload (Cloud API) - implemented but needs testing
- File Upload (Local FTP) - implemented but needs testing

### Implemented (Awaiting Validation)

- Video Streams (RTSP for X1, JPEG for A1/P1)
- Local FTP file upload
- Cloud file upload

## Examples

### Home Automation

Integrate with Home Assistant via the compatibility layer:

```bash
cd servers
python3 compatibility.py
```

Home Assistant configuration:
```yaml
rest:
  - resource: http://localhost:8080/api/v1/status?device_id=YOUR_DEVICE_ID
    scan_interval: 10
    sensor:
      - name: "Bambu Print Progress"
        value_template: "{{ value_json.print.mc_percent }}"
```

### Print Farm Management

```python
for device in api.get_devices():
    status = api.get_print_status(device['dev_id'])
    print(f"{device['name']}: {status['progress']}%")
```

### Real-Time Monitoring

```python
def on_status(device_id, data):
    if data['print']['mc_percent'] == 100:
        send_notification("Print complete!")

mqtt = MQTTClient(uid, token, device_id, on_message=on_status)
mqtt.connect(blocking=True)
```

## Screenshots

### Video Streaming

![P1S Video Stream](screenshots/P1SStream.png)
*Live JPEG frame streaming from P1S printer camera*

### Test Suite Output

The comprehensive test suite provides detailed information about all API endpoints and printer data:

![Test Output Example 1](screenshots/Screenshot1.png)
*Comprehensive test output showing Cloud API tests with device info, firmware versions, and all data fields*

![Test Output Example 2](screenshots/Screenshot2.png)
*MQTT monitoring with real-time printer data including temperatures, fan speeds, and print progress*

![Test Output Example 3](screenshots/Screenshot3.png)
*Complete MQTT data streams showing all available fields from printer status updates*

![Test Output Example 4](screenshots/Screenshot4.png)
*Camera credentials and video streaming configuration with TTCode authentication*

![Test Output Example 5](screenshots/Screenshot5.png)
*File upload testing and cloud storage integration results*

## Disclaimer

This project is **not affiliated with or endorsed by Bambu Lab**. It is an effort to document their API.

- Use at your own risk
- Respect Bambu Lab's Terms of Service
- Don't abuse API rate limits
- Be responsible with printer control

The API may change without notice. This documentation represents the API as of October 2025.


## Ethical & Legal Compliance

**Documents API endpoints to ensure backwards compatibility and interoperability; the necessary information was determined through network traffic analysis of the official client communicating with publicly accessible servers, which complies with fair use principles.**

This analysis:
- Documents publicly accessible API endpoints
- Enables community integrations and home automation
- Complies with fair use for interoperability
- Uses only your own credentials for testing

Does NOT:
- Bypass security measures
- Violate terms of service
- Redistribute proprietary code
- Enable unauthorized access

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see [LICENSE](LICENSE) for details.