# Bambu Lab Cloud API - Device Management

**Last Updated:** 2025-10-25

This document covers device binding, management, print jobs, projects, tasks, and notifications.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

---

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
      "dev_id": "01234567890ABCD",
      "name": "P1S 1",
      "online": true,
      "print_status": "ACTIVE",
      "dev_model_name": "C11",
      "dev_product_name": "P1P",
      "dev_access_code": "012345679"
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
  "device_id": "GLOF01234567901",
  "device_name": "My Printer",
  "bind_code": "01234567"
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
    "device_id": "GLOF01234567901",
    "device_name": "X1 Carbon",
    "model": "X1C",
    "status": "online",
    "firmware_version": "01.01.01.01",
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
    "current_version": "01.01.01.01",
    "latest_version": "01.01.01.01",
    "update_available": true,
    "release_notes": "..."
  }
}
```

**Unbind Device from User**
```http
DELETE /v1/iot-service/api/user/bind?dev_id=<device_id>
Authorization: Bearer <token>

Response:
{
  "code": 0,
  "message": "Device unbound successfully"
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
  "device_id": "GLOF01234567901",
  "file_id": "012345",
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

**Get Project Details**
```http
GET /v1/iot-service/api/user/project/{project_id}

Response:
{
  "code": 0,
  "data": {
    "project_id": "proj_123",
    "name": "My Design",
    "created_at": "2024-10-18T10:00:00Z",
    "updated_at": "2024-10-18T12:00:00Z",
    "file_count": 3,
    "files": [...]
  }
}
```

#### Tasks Management

Tasks represent print jobs and file operations associated with devices.

**Get User Tasks**
```http
GET /v1/user-service/my/tasks
GET /v1/user-service/my/tasks?deviceId=<device_id>&after=<task_id>&limit=20

Parameters:
- deviceId: Filter by device (optional)
- after: Pagination cursor (task ID)
- limit: Results per page (default: 20)

Response:
{
  "tasks": [
    {
      "id": "012345678",
      "designId": "012345678",
      "designTitle": "Cube",
      "deviceId": "01234567890ABCD",
      "deviceName": "P1S 3",
      "modelId": "012345678",
      "profileId": "012345678",
      "status": "failed",
      "weight": 12.5,
      "length": 1850.2,
      "costTime": 3600,
      "startTime": "2024-10-24T10:00:00Z",
      "endTime": "2024-10-24T11:00:00Z",
      "cover": "https://...",
      "thumbnail": "https://..."
    }
  ],
  "hits": {
    "total": {
      "value": 156,
      "relation": "eq"
    }
  }
}
```

**Get Single Task**
```http
GET /v1/iot-service/api/user/task/{task_id}

Response:
{
  "code": 0,
  "data": {
    "task_id": "012345678",
    "device_id": "01234567890ABCD",
    "status": "completed",
    "progress": 100,
    "file_name": "model.3mf",
    "started_at": "2024-10-24T10:00:00Z",
    "completed_at": "2024-10-24T11:00:00Z"
  }
}
```

**Create Task**
```http
POST /v1/user-service/my/task
Content-Type: application/json

Request Body:
{
  "modelId": "012345678",
  "title": "My Print Job",
  "deviceId": "01234567890ABCD",
  "profileId": "012345678"
}

Response:
{
  "id": "012345678",
  "status": "created"
}
```

#### File Upload

**Get Upload URL**
```http
GET /v1/iot-service/api/user/upload
GET /v1/iot-service/api/user/upload?filename=model.3mf&size=012345

Parameters:
- filename: Name of file to upload
- size: File size in bytes

Response:
{
  "message": "success",
  "code": null,
  "error": null,
  "host": "user",
  "urls": [
    {
      "type": "filename",
      "file": "model.3mf",
      "url": "https://s3.us-west-2.amazonaws.com/or-cloud-upload-prod/users/012345678/filename/01234567890ABCDEF0/model.3mf?AWSAccessKeyId=01234567890ABCDEF012&Expires=0123456789&Signature=01234567890ABCDEF01234567890ABCDEF"
    },
    {
      "type": "size",
      "file": "012345",
      "url": "https://s3.us-west-2.amazonaws.com/or-cloud-upload-prod/users/012345678/size/01234567890ABCDEF0/012345?AWSAccessKeyId=01234567890ABCDEF012&Expires=0123456789&Signature=01234567890ABCDEF01234567890ABCD"
    }
  ]
}
```

**Upload to S3 (Step 1: Filename)**
```http
PUT <filename_url_from_above>
Content-Type: application/octet-stream
Content-Length: 012345

<binary_file_data>

Response: 200 OK
```

**Upload to S3 (Step 2: Size)**
```http
PUT <size_url_from_above>
Content-Type: text/plain
Content-Length: 6

012345

Response: 200 OK
```

**Important Notes:**
- Must upload to BOTH URLs (filename AND size) for successful upload
- Use exact Content-Type headers as specified
- URLs are pre-signed by AWS and expire after the time indicated
- Size URL expects the file size as plain text
- Signature mismatch errors typically indicate wrong Content-Type or HTTP method

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


---

## See Also

- [API_USERS.md](API_USERS.md) - User profiles and accounts
- [API_FILES_PRINTING.md](API_FILES_PRINTING.md) - File upload and printing
- [API_MQTT.md](API_MQTT.md) - MQTT protocol and commands
- [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) - AMS and filament data
- [API_CAMERA.md](API_CAMERA.md) - Camera and video streaming
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes and responses
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication methods
