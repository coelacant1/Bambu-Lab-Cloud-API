# BAMBU LAB CLOUD API DOCUMENTATION

**Reconstructed from Bambu Connect:** v2.0.0-beta.7

**Method:** Static analysis + Frontend code extraction

**Last Updated:** 2025-10-18

---

## BASE INFRASTRUCTURE

### Production APIs

**Global (International):**
```
Main API:    https://api.bambulab.com
Portal:      https://e.bambulab.com
Website:     https://bambulab.com
CDN:         https://public-cdn.bblmw.com
```

**China Region:**
```
Main API:    https://api.bambulab.cn
Portal:      https://e.bambulab.cn
Website:     https://bambulab.cn
CDN:         https://public-cdn.bblmw.cn
```

### Development/Testing APIs (Internal)

```
Dev API:      https://api-dev.bambulab.net
Dev Portal:   https://e-dev.bambulab.net
Dev Console:  https://portal-dev.bambulab.net

QA API:       https://api-qa.bambulab.net  
QA Portal:    https://e-qa.bambulab.net
QA Console:   https://portal-qa.bambulab.net

Pre-prod US:  https://api-pre-us.bambulab.net
Pre-prod:     https://api-pre.bambulab.net
Pre Console:  https://portal-pre.bambulab.net
```

### MQTT Brokers

```
US Broker:    us.mqtt.bambulab.com:8883
China Broker: cn.mqtt.bambulab.com:8883
Dev Broker:   dev.mqtt.bambu-lab.com:8883
```

### CDN/Update Servers

```
Minio API:    https://minio-api.bambu-lab.com
Updates:      /bambu-connect/updates
Alt Updates:  /upgrade/bambu-connect/updates
```

---

## API STRUCTURE

### API Version: v1

Base Path: `/v1/`

All endpoints use:
- **Protocol:** HTTPS
- **Content-Type:** application/json
- **Authentication:** Bearer Token

---

## AUTHENTICATION

### Headers Required

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
x-bbl-app-certification-id: <cert_id>
x-bbl-device-security-sign: <signed_timestamp>
```

### Certificate-Based Authentication

The app uses RSA certificate-based signing:
1. App has a device certificate
2. Signs current timestamp with private key
3. Sends signature in `x-bbl-device-security-sign` header
4. Server verifies with public key from certificate

### Token Format

JWT tokens with:
- Algorithm: RS256 (RSA with SHA-256)
- Contains: user_id, permissions, expiration
- Expires: Varies (typically 24 hours)

---

## API ENDPOINTS

### IOT Service (`/v1/iot-service/api/`)

Handles device management, printing, and IoT operations.

#### User Device Management

**Get Bound Devices**
```http
GET /v1/iot-service/api/user/bind

Response:
{
  "message": "success",
  "code": null,
  "error": null,
  "devices": [
    {
      "dev_id": "01S00A000000000",
      "name": "P1S 1",
      "online": true,
      "print_status": "ACTIVE",
      "dev_model_name": "C11",
      "dev_product_name": "P1P",
      "dev_access_code": "123456789"
    }
  ]
}
```

**Bind Device to User**
```http
POST /v1/iot-service/api/user/bind
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
  "device_id": "GLOF12345678901",
  "device_name": "My Printer",
  "bind_code": "12345678"
}

Response:
{
  "code": 0,
  "message": "Success",
  "data": {
    "bind_id": "...",
    "device_info": {...}
  }
}
```

**Get Device Information**
```http
GET /v1/iot-service/api/user/device/info
GET /v1/iot-service/api/user/device/info?device_id<device_id>

Response:
{
  "code": 0,
  "data": {
    "device_id": "GLOF12345678901",
    "device_name": "X1 Carbon",
    "model": "X1C",
    "status": "online",
    "firmware_version": "01.07.00.00",
    "nozzle_temp": 220,
    "bed_temp": 60,
    ...
  }
}
```

**Get Device Version**
```http
GET /v1/iot-service/api/user/device/version
GET /v1/iot-service/api/user/device/version?device_id<device_id>

Response:
{
  "code": 0,
  "data": {
    "current_version": "01.07.00.00",
    "latest_version": "01.08.00.00",
    "update_available": true,
    "release_notes": "..."
  }
}
```

#### Printing Operations

**Get Print Jobs**
```http
GET /v1/iot-service/api/user/print
GET /v1/iot-service/api/user/print?device_id<device_id>
GET /v1/iot-service/api/user/print?statusprinting|completed|failed

Response:
{
  "code": 0,
  "data": {
    "jobs": [
      {
        "job_id": "12345",
        "file_name": "model.3mf",
        "status": "printing",
        "progress": 45,
        "time_remaining": 3600,
        "started_at": "2024-10-18T10:00:00Z"
      }
    ]
  }
}
```

**Start Print Job**
```http
POST /v1/iot-service/api/user/print
Content-Type: application/json

Request Body:
{
  "device_id": "GLOF12345678901",
  "file_id": "abc123",
  "file_name": "model.3mf",
  "file_url": "https://...",
  "settings": {
    "layer_height": 0.2,
    "infill": 20,
    "speed": 100
  }
}

Response:
{
  "code": 0,
  "data": {
    "job_id": "12345",
    "status": "queued"
  }
}
```

#### Project Management

**Get Projects**
```http
GET /v1/iot-service/api/user/project
GET /v1/iot-service/api/user/project?page1&limit20

Response:
{
  "code": 0,
  "data": {
    "projects": [
      {
        "project_id": "proj_123",
        "name": "My Design",
        "created_at": "2024-10-18T10:00:00Z",
        "file_count": 3
      }
    ],
    "total": 45,
    "page": 1
  }
}
```

#### File Upload

**Upload File**
```http
POST /v1/iot-service/api/user/upload
Content-Type: multipart/form-data

Request Body:
- file: <binary_data>
- filename: "model.3mf"
- project_id: "proj_123" (optional)

Response:
{
  "code": 0,
  "data": {
    "file_id": "file_abc123",
    "file_url": "https://...",
    "file_size": 1048576
  }
}
```

#### Notifications

**Get Notifications**
```http
GET /v1/iot-service/api/user/notification
GET /v1/iot-service/api/user/notification?unreadtrue

Response:
{
  "code": 0,
  "data": {
    "notifications": [
      {
        "id": "notif_123",
        "type": "print_complete",
        "message": "Print job completed successfully",
        "timestamp": "2024-10-18T10:00:00Z",
        "read": false
      }
    ]
  }
}
```

**Mark Notification as Read**
```http
PUT /v1/iot-service/api/user/notification
Content-Type: application/json

Request Body:
{
  "notification_id": "notif_123",
  "read": true
}
```

---

### User Service (`/v1/user-service/`)

Handles user account and profile management.

#### User Profile

**Get User Preferences**
```http
GET /v1/design-user-service/my/preference

Response:
{
  "uid": 123456789,
  "name": "user_123456789",
  "handle": "user_123456789",
  "avatar": "url",
  "bio": "",
  "links": [],
  "backgroundUrl": "url"
}
```

**Get My Profile**
```http
GET /v1/user-service/my/profile

Response:
{
  "code": 0,
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "username": "JohnDoe",
    "avatar_url": "https://...",
    "created_at": "2024-01-01T00:00:00Z",
    "subscription": {
      "plan": "pro",
      "expires_at": "2025-01-01T00:00:00Z"
    }
  }
}
```

**Update Profile**
```http
PUT /v1/user-service/my/profile
Content-Type: application/json

Request Body:
{
  "username": "NewUsername",
  "avatar_url": "https://..."
}

Response:
{
  "code": 0,
  "message": "Profile updated"
}
```

#### User Messages

**Get My Messages**
```http
GET /v1/user-service/my/messages
GET /v1/user-service/my/messages?type<type>&after<id>&limit20

Response:
{
  "hits": [
    {
      "id": 0,
      "type": 6,
      "taskMessage": {
        "id": 1,
        "title": "Untitled",
        "cover": "https://...",
        "status": 2,
        "deviceId": "..."
      },
      "from": {
        "uid": 2,
        "name": "User",
        "avatar": "https://..."
      },
      "createTime": "2022-11-22T02:54:12Z"
    }
  ]
}
```

#### User Tasks

**Get My Tasks**
```http
GET /v1/user-service/my/tasks
GET /v1/user-service/my/tasks?deviceId<device_id>&after<id>&limit20

Response:
{
  "total": 5,
  "hits": [
    {
      "id": 0,
      "designId": 0,
      "modelId": "...",
      "title": "Untitled",
      "cover": "https://...",
      "status": 2,
      "feedbackStatus": 0,
      "startTime": "2022-11-22T01:58:10Z",
      "endTime": "2022-11-22T02:54:12Z",
      "weight": 12.6,
      "costTime": 3348,
      "profileId": 0,
      "plateIndex": 1,
      "deviceId": "...",
      "amsDetailMapping": [],
      "mode": "cloud_file"
    }
  ]
}
```

**Create Task**
```http
POST /v1/user-service/my/task
Content-Type: application/json

Request Body:
{
  "modelId": "...",
  "title": "Print Job",
  "deviceId": "...",
  ...
}
```

**Get Task by ID**
```http
GET /v1/iot-service/api/user/task/{task_id}
```

---

### Account Service (`/v1/accounts/`)

Account management and authentication.

**Login/Authentication:**
```http
POST /v1/user-service/user/login
POST /v1/user-service/user/refreshtoken
```

**Expected endpoints (not directly confirmed but standard):**
```http
POST /v1/accounts/login
POST /v1/accounts/logout
POST /v1/accounts/refresh
POST /v1/accounts/register
POST /v1/accounts/reset-password
```

---

### Certificate Service

Based on the old code analysis:

**Get Certificate**
```http
GET /v1/cert/get
Authorization: Bearer <token>

Response:
{
  "key": "<base64_encrypted_private_key>",
  "cert": "-----BEGIN CERTIFICATE-----...",
  "crl": ["-----BEGIN X509 CRL-----..."]
}
```

**Update Certificate**
```http
POST /v1/cert/update
Content-Type: application/json

Request Body:
{
  "cert": "-----BEGIN CERTIFICATE-----...",
  "cert_id": "..."
}
```

---

## MQTT PROTOCOL

### Connection

```
Broker:   us.mqtt.bambulab.com
Port:     8883 (TLS)
Protocol: MQTT 3.1.1 / 5.0

Authentication:
- Username: <user_id>
- Password: <mqtt_token>
- TLS: Required
```

### Topic Structure

**Subscribe to device updates:**
```
device/<device_id>/report
device/<device_id>/status
printer/<device_id>/state
```

**Publish commands:**
```
device/<device_id>/request
printer/<device_id>/command
```

### Message Format

```json
{
  "print": {
    "command": "start|pause|stop|resume",
    "sequence_id": "12345",
    "param": {
      "file_url": "https://...",
      "file_name": "model.3mf"
    }
  }
}
```

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

## EXAMPLES

### Complete Request Example

```bash
curl -X GET "https://api.bambulab.com/v1/iot-service/api/user/device/info?device_idGLOF12345678901" \
  -H "Authorization: Bearer fascvj789VHXDKJVfs7fs9f9..." \
  -H "Content-Type: application/json" \
  -H "x-bbl-app-certification-id: GLOF12345678901:12345678901" \
  -H "x-bbl-device-security-sign: cvhx78xVF78vxhjksdHSjdkjhfksd..."
```

### Python Example

```python
import requests

BASE_URL  "https://api.bambulab.com/v1"
TOKEN  "your_bearer_token"

headers  {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "x-bbl-app-certification-id": "your_cert_id",
    "x-bbl-device-security-sign": "your_signature"
}

# Get device info
response  requests.get(
    f"{BASE_URL}/iot-service/api/user/device/info",
    headersheaders,
    params{"device_id": "GLOF12345678901"}
)

print(response.json())
```



