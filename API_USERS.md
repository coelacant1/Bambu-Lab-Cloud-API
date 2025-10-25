# Bambu Lab Cloud API - User Management

**Last Updated:** 2025-10-25

This document covers user profiles, preferences, messages, and account management.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

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
  "name": "user_012345678",
  "handle": "user_012345678",
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
    "user_id": "user_012",
    "email": "0123@01234567890",
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

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management
- [API_FILES_PRINTING.md](API_FILES_PRINTING.md) - File upload and printing
- [API_MQTT.md](API_MQTT.md) - MQTT protocol
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
