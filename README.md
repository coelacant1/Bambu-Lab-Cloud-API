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
- **Authentication with 2FA** - Automatic login with email verification code support
- **MQTT Support** - Real-time printer monitoring and control
- **File Upload** - Cloud API and local FTP upload support
- **Video Streaming** - RTSP (X1 series) and JPEG frame streaming (A1/P1 series)
- **Compatibility Layer** - Restore legacy local API without developer mode
- **Proxy Servers** - Safe API gateways (strict read-only and full modes)
- **Testing Suite** - Comprehensive unit tests for all functionality
- **G-code Reference** - Command documentation for printer models

![P1S Video Stream](screenshots/P1SStream.png)
*Live JPEG frame streaming from P1S printer camera*

## Quick Start: Authentication

### Get Your Access Token

```bash
# Interactive login with 2FA support
python cli_tools/login.py

# Or non-interactive
python cli_tools/login.py --username user@email.com --password yourpass
```

The tool will:
1. Submit your credentials to Bambu Lab
2. Request email verification code
3. Prompt you to enter the code from your email
4. Save the token to `~/.bambu_token` for future use

## Quick Test (Automated)

Test all functionality with the comprehensive test suite:

```bash
cd tests
cp test_config.json.example test_config.json
# Edit test_config.json with your credentials
python3 test_comprehensive.py
```

**Test Coverage:**
- Cloud API (20 endpoints tested)
- MQTT real-time monitoring
- Video streaming credentials
- File upload to cloud
- AMS filament data
- Device management

**Recent Test Results:** 20/20 tests passing
- All Cloud API endpoints working
- MQTT live data streaming confirmed
- File upload to S3 verified
- TUTK video credentials obtained



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
# Install from PyPI (includes all features)
pip install bambu-lab-cloud-api

# Or install latest from GitHub
pip install git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git
```

**v1.0.4+** includes everything by default:
- Cloud API client
- MQTT support
- Camera streaming
- Proxy servers with rate limiting
- CLI tools

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Authentication

```python
from bambulab import BambuAuthenticator, BambuClient

# Authenticate with 2FA support
auth = BambuAuthenticator()
token = auth.login("your-email@example.com", "your-password")
# ^ Will prompt for email verification code

# Or use saved token (auto-refresh if needed)
token = auth.get_or_create_token(
    username="your-email@example.com",
    password="your-password"
)

# Use token with client
client = BambuClient(token=token)
```

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

Command-line utilities for quick printer access:

| Tool | Purpose |
|------|---------|
| `bambu-query` | Query printer information and status |
| `bambu-monitor` | Real-time MQTT monitoring |
| `bambu-camera` | View live camera feed |

After installation, use directly:
```bash
bambu-query YOUR_TOKEN --devices
bambu-monitor YOUR_UID YOUR_TOKEN YOUR_DEVICE_ID
bambu-camera YOUR_TOKEN --ip 192.168.1.100
```

See [cli_tools/README.md](cli_tools/README.md) for detailed usage.

## Verified Features

Based on comprehensive testing (see test output):

### Cloud API (Fully Working)
- **Device Management** - List devices, get info, firmware versions
- **User Profile** - Account information, owned printer models
- **AMS/Filament** - Filament data from AMS units
- **Camera Credentials** - TTCode for P2P video streaming (TUTK protocol)
- **File Upload** - Cloud file upload via S3 signed URLs
- **File Management** - List and manage cloud files

### MQTT Real-Time (Fully Working)
- **Connection** - Stable MQTT connection to printers
- **Live Status** - Real-time temperature, progress, state updates
- **Full Data** - Complete printer state including:
  - Temperatures (nozzle, bed, chamber)
  - Print progress and layer info
  - Fan speeds and print speeds
  - AMS status and filament data
  - Error codes (HMS)
  - Network info (WiFi signal)

### Video Streaming (Working)
- **TUTK Protocol** - P2P video credentials for local streaming
- **TTCode Generation** - Authentication for camera access
- **Multi-Model Support** - P1/A1 (JPEG), X1 (RTSP)

### Partially Tested
- **Local FTP Upload** - Implemented, requires local network testing
- **Compatibility Layer** - Lightly tested, works with legacy tools

### Not Yet Implemented
- Print job submission via API
- Device control commands (pause, resume, stop)
- Some write operations (device settings)

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

The API may change without notice. This documentation represents the API as of **October 2025** based on testing with firmware versions **01.08.02.00** and **01.09.00.00**.

**Tested Configurations:**
- Printer Models: P1P, P1S
- Firmware: 01.08.02.00, 01.09.00.00
- Python: 3.9-3.13
- Test Suite: 20/20 passing (Full testing with 3.13)


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