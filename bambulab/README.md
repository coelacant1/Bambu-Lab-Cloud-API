# Bambu Lab Python Library

**Last Updated:** October 25, 2025

A unified Python library for interacting with Bambu Lab 3D printers via Cloud API and MQTT.

## Features

- **HTTP API Client**: Full access to Bambu Lab Cloud API
- **MQTT Client**: Real-time printer monitoring and control
- **Video Streaming**: Access printer cameras (X1 RTSP, A1/P1 JPEG)
- **Local API**: Direct FTP file upload and local printing
- **File Upload**: Upload 3MF/gcode files to cloud or printer
- **Token Management**: Secure token storage and validation
- **Data Models**: Structured data classes for devices and status
- **Utility Functions**: Common helpers for data formatting

## Installation

```bash
# Install required dependencies
pip install requests paho-mqtt flask flask-cors
```

## Quick Start

### HTTP API Client

```python
from bambulab import BambuClient

# Initialize client
client = BambuClient(token="your_bambu_token")

# Get devices
devices = client.get_devices()
for device in devices:
    print(f"{device['name']}: {device['print_status']}")

# Get print status
status = client.get_print_status()
print(status)
```

### MQTT Monitoring

```python
from bambulab import MQTTClient

def on_message(device_id, data):
    print(f"Device {device_id}: {data['print']['gcode_state']}")

# Initialize MQTT client
mqtt = MQTTClient(
    username="your_uid",
    access_token="your_token",
    device_id="device_serial",
    on_message=on_message
)

# Connect and monitor
mqtt.connect(blocking=True)
```

### Token Management

```python
from bambulab import TokenManager

# Initialize token manager
tm = TokenManager("tokens.json")

# Add token mapping
tm.add_token("my-custom-token", "real_bambu_token")

# Validate token
real_token = tm.validate("my-custom-token")
```

## Modules

### `client.py`
HTTP API client for Bambu Lab Cloud API. Handles authentication, requests, and response parsing.

**Key Classes:**
- `BambuClient`: Main API client

**Methods:**

*Device Management:*
- `get_devices()`: Get list of printers
- `get_device_version(device_id)`: Get firmware version for device
- `get_device_versions()`: Get firmware versions for all devices
- `get_device_info(device_id)`: Get detailed device information
- `bind_device(device_id, name, code)`: Bind new device to account
- `unbind_device(device_id)`: Unbind device from account

*Print Status:*
- `get_print_status(force=False)`: Get current print status
- `get_tasks()`: Get list of print tasks

*User Management:*
- `get_user_profile()`: Get user profile information
- `get_user_info()`: Get user preference/info (includes UID for MQTT)
- `update_user_profile(data)`: Update user profile

*Project Management:*
- `get_projects()`: Get list of projects
- `get_project(project_id)`: Get specific project details
- `create_project(name, **kwargs)`: Create new project

*Camera/Webcam Access:*
- `get_camera_credentials(device_id)`: Get webcam access credentials
- `get_ttcode(device_id)`: Alias for get_camera_credentials()

*Notifications & Messages:*
- `get_notifications(action=None, unread_only=False)`: Get notifications
- `get_messages(type=None, after=None, limit=20)`: Get user messages

*Slicer Settings:*
- `get_slicer_settings(version=None, setting_id=None)`: Get slicer settings
- `get_slicer_resources(type=None, version=None)`: Get slicer resources

*Utilities:*
- `get_upload_url()`: Get upload URL information
- `upload_file(file_path, filename=None, project_id=None)`: Upload file to cloud

### `video.py`
Video/webcam streaming support for different printer models.

**Key Classes:**
- `RTSPStream`: RTSP stream handler for X1 series
- `JPEGFrameStream`: JPEG frame stream for A1/P1 series

**Functions:**
- `get_video_stream(printer_ip, access_code, model)`: Get appropriate stream handler

**Example:**
```python
from bambulab import JPEGFrameStream

# A1/P1 series JPEG stream
stream = JPEGFrameStream("192.168.1.100", "12345678")
stream.connect()
frame = stream.get_frame()
with open('camera.jpg', 'wb') as f:
    f.write(frame)
stream.disconnect()

# Or use context manager
with JPEGFrameStream("192.168.1.100", "12345678") as stream:
    for frame in stream.stream_frames():
        # Process frames continuously
        pass
```

**X1 Series RTSP:**
```python
from bambulab import RTSPStream

stream = RTSPStream("192.168.1.100", "12345678")
url = stream.get_stream_url()
# Use with VLC, ffmpeg, OpenCV, etc.
```

### `local_api.py`
Local network API for direct printer communication.

**Key Classes:**
- `LocalFTPClient`: FTP client for file uploads
- `LocalPrintClient`: Helper for print commands

**Functions:**
- `upload_and_print()`: Convenience function to upload and start printing

**Example:**
```python
from bambulab import LocalFTPClient, LocalPrintClient, MQTTClient

# Upload file via FTP
with LocalFTPClient("192.168.1.100", "12345678") as ftp:
    result = ftp.upload_file("model.3mf")
    print(f"Uploaded: {result['filename']}")

# Send print command via MQTT
mqtt = MQTTClient("uid", "token", "device_serial")
mqtt.connect()
cmd = LocalPrintClient.create_print_command("/model.3mf", use_ams=True)
mqtt.publish_command(cmd)

# Or use convenience function
from bambulab import upload_and_print

result = upload_and_print(
    "192.168.1.100",
    "12345678", 
    "model.3mf",
    mqtt_client=mqtt,
    use_ams=True
)
```

### `mqtt.py`
MQTT client wrapper for real-time printer monitoring.

**Key Classes:**
- `MQTTClient`: Single-device MQTT monitor
- `MQTTBridge`: Multi-device MQTT bridge

**Authentication Note:**
- Username for cloud MQTT must be prefixed with `u_` (e.g., `u_123456789`)
- The library automatically adds this prefix if not present

**Methods:**
- `connect(blocking=False)`: Connect to MQTT broker
- `disconnect()`: Disconnect from broker
- `publish(command)`: Send commands to device
- `request_full_status()`: Request complete printer status (pushall command)
- `get_last_data()`: Get most recent data received

### `auth.py`
Token management and authentication.

**Key Classes:**
- `TokenManager`: Manage token mappings

**Methods:**
- `add_token()`: Add token mapping
- `validate()`: Validate and retrieve real token
- `list_tokens()`: List all tokens

### `models.py`
Data models for devices and status.

**Key Classes:**
- `Device`: Printer device information
- `PrinterStatus`: Current printer status
- `Project`: Project information

### `utils.py`
Common utility functions.

**Functions:**
- `format_timestamp()`: Format datetime objects
- `format_temperature()`: Format temperature values
- `format_time_remaining()`: Format time in human-readable format
- `parse_device_data()`: Parse and normalize device data


