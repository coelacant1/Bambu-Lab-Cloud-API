# Bambu Lab Cloud API - Reference

**Last Updated:** 2025-10-25

This document covers response codes, error handling, rate limiting, pagination, and API conventions.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

---

## RESPONSE CODES

### Standard Response Format

```json
{
  "code": 0,
  "message": "Success",
  "data": { ... }
}
```

### Common Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 429  | Too Many Requests |
| 500  | Internal Server Error |

### Application-Specific Codes

| Code | Meaning |
|------|---------|
| 1001 | Invalid Token |
| 1002 | Token Expired |
| 1003 | Device Not Found |
| 1004 | Device Offline |
| 1005 | Print Job Failed |
| 1006 | File Upload Failed |

---

## ERROR HANDLING

### Error Response Format

```json
{
  "code": 1001,
  "message": "Invalid token",
  "error": "TOKEN_INVALID",
  "details": {
    "reason": "Token signature verification failed"
  }
}
```

### Error Codes Found in Code

```
ERR_NETWORK
ERR_INVALID_URL
ERR_BAD_REQUEST
ERR_BAD_RESPONSE
ERR_CANCELED
ERR_CHECKSUM_MISMATCH
ERR_FR_TOO_MANY_REDIRECTS
ERR_UPDATER_INVALID_VERSION
```

---

## RATE LIMITING

Expected limits (based on standard practices):
- **Authenticated:** 1000 requests/hour
- **Device Status:** 10 requests/minute per device
- **File Upload:** 10 uploads/hour
- **MQTT:** 100 messages/minute

---

## PAGINATION

Standard pagination parameters:
```http
GET /endpoint?page1&limit20&offset0

Response includes:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "has_more": true
  }
}
```

---

## FILE OPERATIONS

### Upload Flow

1. **Request upload URL:**
```http
POST /v1/iot-service/api/user/upload
Response: { "upload_url": "https://..." }
```

2. **Upload file to S3/CDN:**
```http
PUT <upload_url>
Content-Type: application/octet-stream
Body: <file_data>
```

3. **Confirm upload:**
```http
POST /v1/iot-service/api/user/upload/confirm
Body: { "file_id": "..." }
```

### Supported File Types

- `.3mf` - 3D Model Format
- `.gcode` - G-Code
- `.stl` - STereoLithography
- `.step` - STEP CAD format

---

## WEBHOOKS

The API likely supports webhooks for events:
```
print.started
print.completed
print.failed
device.online
device.offline
notification.created
```

---

## TESTING

### Test Environments

**Dev:**
```
API: https://api-dev.bambulab.net
```

**QA:**
```
API: https://api-qa.bambulab.net
```

**Pre-production:**
```
API: https://api-pre.bambulab.net
API US: https://api-pre-us.bambulab.net
```

---

## MQTT DEVICE COMMANDS

The following MQTT commands can be sent to control printer devices via the MQTT broker.

**Topic Format:** `device/{device_id}/request`

### Print Control Commands

#### Pause Print

**Command:**
```json
{
  "print": {
    "command": "pause"
  }
}
```

**Description:** Pauses the current print job.

---

#### Resume Print

**Command:**
```json
{
  "print": {
    "command": "resume"
  }
}
```

**Description:** Resumes a paused print job.

---

#### Stop Print

**Command:**
```json
{
  "print": {
    "command": "stop"
  }
}
```

**Description:** Stops the current print job.

---

### Temperature Control Commands

#### Set Nozzle Temperature

**Command:**
```json
{
  "print": {
    "command": "set_nozzle_temp",
    "param": "<temperature_celsius>"
  }
}
```

**Parameters:**
- `param` (integer): Target nozzle temperature in Celsius (e.g., 220)

**Description:** Sets the target nozzle/hotend temperature.

---

#### Set Bed Temperature

**Command:**
```json
{
  "print": {
    "command": "set_bed_temp",
    "param": "<temperature_celsius>"
  }
}
```

**Parameters:**
- `param` (integer): Target bed temperature in Celsius (e.g., 60)

**Description:** Sets the target heated bed temperature.

---

#### Set Chamber Temperature

**Command:**
```json
{
  "print": {
    "command": "set_chamber_temp",
    "param": "<temperature_celsius>"
  }
}
```

**Parameters:**
- `param` (integer): Target chamber temperature in Celsius (e.g., 35)

**Description:** Sets the target chamber temperature (for printers with heated chambers).

---

### Fan Control Commands

#### Set Fan Speed

**Command:**
```json
{
  "print": {
    "command": "set_fan_speed",
    "param": "<speed_percentage>"
  }
}
```

**Parameters:**
- `param` (integer): Fan speed percentage 0-100

**Description:** Sets the part cooling fan speed.

---

#### Set Air Duct Fan

**Command:**
```json
{
  "print": {
    "command": "set_airduct",
    "param": "<speed_percentage>"
  }
}
```

**Parameters:**
- `param` (integer): Air duct fan speed percentage 0-100

**Description:** Controls the air duct/auxiliary fan speed.

---

#### Set Chamber Fan (CTT)

**Command:**
```json
{
  "print": {
    "command": "set_ctt",
    "param": "<speed_percentage>"
  }
}
```

**Parameters:**
- `param` (integer): Chamber fan speed percentage 0-100

**Description:** Sets the chamber temperature control fan speed.

---

### MQTT Command Examples

**Python example using paho-mqtt:**

```python
import json
import paho.mqtt.client as mqtt

# Connection details
BROKER = "us.mqtt.bambulab.com"
PORT = 8883
DEVICE_ID = "your_device_id"
ACCESS_CODE = "your_access_code"

# Create MQTT client
client = mqtt.Client()
client.username_pw_set(username="bblp", password=ACCESS_CODE)
client.tls_set()

# Connect to broker
client.connect(BROKER, PORT, 60)

# Send pause command
topic = f"device/{DEVICE_ID}/request"
command = {"print": {"command": "pause"}}
client.publish(topic, json.dumps(command))

# Send temperature command
command = {"print": {"command": "set_nozzle_temp", "param": "220"}}
client.publish(topic, json.dumps(command))

client.disconnect()
```

---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management
- [API_USERS.md](API_USERS.md) - User profiles
- [API_FILES_PRINTING.md](API_FILES_PRINTING.md) - File upload
- [API_MQTT.md](API_MQTT.md) - MQTT protocol
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
