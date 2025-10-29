# Bambu Lab Cloud API - Documentation Index

**Last Updated:** 2025-10-25  
**Status:** Complete and Modular

This is the master index for all Bambu Lab Cloud API documentation. The documentation has been split into focused, logical modules for easier navigation and reference.

---

## Quick Start

1. **Start Here:** [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Learn how to authenticate
2. **Get Devices:** [API_DEVICES.md](API_DEVICES.md) - Bind and manage your printers
3. **Upload Files:** [API_FILES_PRINTING.md](API_FILES_PRINTING.md) - Upload 3MF files and start prints
4. **Real-time Control:** [API_MQTT.md](API_MQTT.md) - Use MQTT for live printer control

---

## Documentation Modules

### Core API Documentation

| Document | Focus Area | Lines | Description |
|----------|-----------|-------|-------------|
| [API_AUTHENTICATION.md](API_AUTHENTICATION.md) | Auth & Security | 387 | Authentication methods, JWT tokens, certificate signing, and security best practices |
| [API_DEVICES.md](API_DEVICES.md) | Device Management | 411 | Binding devices, getting device info, print jobs, projects, tasks, and notifications |
| [API_USERS.md](API_USERS.md) | User Accounts | 173 | User profiles, preferences, messages, and account management |
| [API_FILES_PRINTING.md](API_FILES_PRINTING.md) | Files & Printing | 411 | Cloud file upload (S3), managing files, starting cloud prints, and troubleshooting |
| [API_MQTT.md](API_MQTT.md) | Real-time Protocol | 255 | MQTT connection, topics, message formats, device commands, and monitoring |
| [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) | AMS & Materials | 414 | AMS unit data, filament information, colors, types, and real-time monitoring |
| [API_CAMERA.md](API_CAMERA.md) | Video Streaming | 343 | Camera credentials, TUTK P2P protocol, video streaming, and local JPEG access |
| [API_REFERENCE.md](API_REFERENCE.md) | Standards & Codes | 399 | Response codes, error handling, rate limiting, pagination, and conventions |

---

## Documentation by Use Case

### Setting Up Access

1. [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Get your Bearer token
2. [API_USERS.md](API_USERS.md) - Verify your profile
3. [API_DEVICES.md](API_DEVICES.md) - Bind your printer to your account

### Uploading and Printing

1. [API_FILES_PRINTING.md](API_FILES_PRINTING.md) - Upload 3MF files to cloud
2. [API_DEVICES.md](API_DEVICES.md) - Start print job on device
3. [API_MQTT.md](API_MQTT.md) - Monitor print progress in real-time

### Real-time Monitoring

1. [API_MQTT.md](API_MQTT.md) - Connect to MQTT broker
2. [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) - Monitor filament levels
3. [API_CAMERA.md](API_CAMERA.md) - View live camera feed

### Advanced Control

1. [API_MQTT.md](API_MQTT.md) - Send control commands (pause, resume, stop)
2. [API_DEVICES.md](API_DEVICES.md) - Manage multiple printers
3. [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) - Read AMS sensor data

---

## API Endpoints Overview

### Base URLs

**Global (International):**
- REST API: `https://api.bambulab.com`
- MQTT: `us.mqtt.bambulab.com:8883`

**China Region:**
- REST API: `https://api.bambulab.cn`
- MQTT: `cn.mqtt.bambulab.com:8883`

### Endpoint Structure

All REST API endpoints follow the pattern:
```
https://api.bambulab.com/v1/{service}/{resource}
```

**Services:**
- `/v1/iot-service/api/` - Device and IoT operations
- `/v1/user-service/` - User account management
- `/v1/design-user-service/` - Design and preferences

---

## Response Format Standards

All API responses follow this structure:

```json
{
  "message": "success",
  "code": null,
  "error": null,
  "data": { ... }
}
```

Or for newer endpoints:

```json
{
  "code": 0,
  "message": "Success",
  "data": { ... }
}
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete response code documentation.

---

## Authentication Quick Reference

All authenticated requests require:

```http
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json
```

Optional security headers:
```http
x-bbl-app-certification-id: YOUR_CERT_ID
x-bbl-device-security-sign: SIGNED_TIMESTAMP
```

Full details: [API_AUTHENTICATION.md](API_AUTHENTICATION.md)

---

## MQTT Quick Reference

**Connection:**
```
Host: us.mqtt.bambulab.com
Port: 8883 (TLS)
Username: u_{your_user_id}
Password: {device_access_code}
```

**Topic Structure:**
```
device/{device_serial}/report    (subscribe - receive updates)
device/{device_serial}/request   (publish - send commands)
```

Full details: [API_MQTT.md](API_MQTT.md)

---

## Data Models

### Device Object

```json
{
  "dev_id": "01234567890ABCD",
  "name": "P1S 1",
  "online": true,
  "print_status": "ACTIVE",
  "dev_model_name": "C11",
  "dev_product_name": "P1P",
  "dev_access_code": "01234567"
}
```

See [API_DEVICES.md](API_DEVICES.md) for complete device data structure.

### Task Object

```json
{
  "id": "012345678",
  "designTitle": "My Print",
  "deviceId": "01234567890ABCD",
  "status": "completed",
  "progress": 100,
  "startTime": "2024-10-24T10:00:00Z",
  "endTime": "2024-10-24T11:00:00Z"
}
```

See [API_DEVICES.md](API_DEVICES.md) for task management.

### AMS Object

```json
{
  "ams": [{
    "id": "0",
    "humidity": "3",
    "temp": "25.0",
    "tray": [
      {
        "id": "1",
        "tray_type": "PETG",
        "tray_color": "FF0000FF",
        "remain": 85
      }
    ]
  }]
}
```

See [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) for AMS data structure.

---

## Python Client Library

This repository includes a Python client library for easy API access:

```python
from bambulab.bambuclient import BambuClient

# Initialize client
client = BambuClient(token="your_token_here", region="global")

# Get devices
devices = client.get_devices()
print(f"Found {len(devices)} printers")

# Get device info
info = client.get_device_info(device_id="01234567890ABCD")
print(f"Status: {info['status']}")

# Upload file
result = client.upload_file("model.3mf", "/path/to/model.3mf")
print(f"Uploaded: {result['success']}")

# Start print
client.start_cloud_print(
    device_id="01234567890ABCD",
    file_id="model_id",
    file_name="model.3mf"
)
```

See the `/bambulab/` directory for full client implementation.

---

## Testing

Comprehensive test suite available in `/tests/`:

```bash
# Run all tests
python tests/manual/test_comprehensive.py

# Test specific functionality
python tests/unit/test_mqtt.py
python tests/unit/test_upload.py
```

Tests cover:
- Authentication and token validation
- Device binding and management
- File upload to S3
- Cloud print starting
- MQTT connection and commands
- AMS data retrieval
- Camera credential fetching

---

## Common Workflows

### Workflow 1: Upload and Print

```python
# 1. Get devices
devices = client.get_devices()
device_id = devices[0]['dev_id']

# 2. Upload file
upload_result = client.upload_file("model.3mf", "/path/to/model.3mf")

# 3. Start print
client.start_cloud_print(
    device_id=device_id,
    file_name="model.3mf"
)

# 4. Monitor via MQTT
mqtt_client.connect(device_id)
mqtt_client.subscribe_status()
```

See [API_FILES_PRINTING.md](API_FILES_PRINTING.md) for detailed workflow.

### Workflow 2: Monitor Print Progress

```python
# 1. Connect to MQTT
mqtt = BambuMQTT(user_id, device_serial, access_code)
mqtt.connect()

# 2. Subscribe to status
def on_status(data):
    print(f"Progress: {data['mc_percent']}%")
    print(f"Nozzle: {data['nozzle_temper']}C")
    print(f"Bed: {data['bed_temper']}C")

mqtt.on_message = on_status
mqtt.subscribe_status()

# 3. Keep listening
mqtt.loop_forever()
```

See [API_MQTT.md](API_MQTT.md) for real-time monitoring.

### Workflow 3: Check Filament Levels

```python
# Via MQTT (real-time)
mqtt.connect()
status = mqtt.get_full_status()

for ams in status['ams']['ams']:
    for tray in ams['tray']:
        if 'tray_type' in tray:
            print(f"Tray {tray['id']}: {tray['tray_type']}")
            print(f"  Remaining: {tray['remain']}%")
            print(f"  Color: {tray['tray_color']}")
```

See [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) for filament monitoring.

---

## Error Handling

Standard error response:

```json
{
  "code": 400,
  "message": "Bad Request",
  "error": "Invalid device ID format"
}
```

Common error codes:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

See [API_REFERENCE.md](API_REFERENCE.md) for complete error code documentation.

---

## Rate Limits

| Endpoint Category | Rate Limit | Window |
|-------------------|------------|--------|
| Authentication | 5 requests | 1 minute |
| Device Queries | 120 requests | 1 minute |
| File Upload | 10 uploads | 1 hour |
| MQTT Connections | 5 connections | 5 minutes |
| User Profile | 60 requests | 1 minute |

See [API_REFERENCE.md](API_REFERENCE.md) for detailed rate limiting.

---

**Quick Links:**
- [Authentication](API_AUTHENTICATION.md)
- [Devices](API_DEVICES.md)
- [Users](API_USERS.md)
- [Files & Printing](API_FILES_PRINTING.md)
- [MQTT](API_MQTT.md)
- [AMS & Filament](API_AMS_FILAMENT.md)
- [Camera](API_CAMERA.md)
- [Reference](API_REFERENCE.md)
