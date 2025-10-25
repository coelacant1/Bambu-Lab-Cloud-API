# Bambu Lab Cloud API - Files & Cloud Printing

**Last Updated:** 2025-10-25

This document covers file upload to cloud storage, cloud file management, starting cloud prints, and troubleshooting.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn  
**S3 Upload:** https://s3.us-west-2.amazonaws.com/or-cloud-upload-prod/

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

---

## CLOUD FEATURES

### Cloud Files and Printing

After uploading files to Bambu Cloud, you can list files and start remote prints.

#### List Cloud Files

```python
from bambulab import BambuClient

client = BambuClient("YOUR_TOKEN")

# Get all files in cloud storage
files = client.get_cloud_files()

for f in files:
    print(f"File: {f['name']}")
    print(f"ID: {f.get('file_id')}")
    print(f"URL: {f.get('file_url')}")
```

**What it does:**
- Searches multiple endpoints for your files
- Returns projects, tasks, uploaded files
- Shows file names, IDs, URLs

#### Start Cloud Print

```python
# Start a print from uploaded file
result = client.start_cloud_print(
    device_id="01234567890ABCD",
    filename="api_test.3mf"
)

print(f"Print started: {result}")
```

**What it does:**
- Finds the file by name in cloud storage
- Starts printing on specified device
- Returns print job information

#### Manual Print Start

If you know the file ID:

```python
result = client.start_print_job(
    device_id="01234567890ABCD",
    file_id="012345",
    file_name="model.3mf",
    file_url="https://...",  # Optional
    settings={
        "layer_height": 0.2,
        "infill": 20,
        "speed": 100
    }
)
```

#### Complete Upload and Print Workflow

```python
from bambulab import BambuClient
import time

client = BambuClient("YOUR_TOKEN")

# Step 1: Upload file
print("Uploading file...")
result = client.upload_file("my_model.3mf")

if result['status_code'] in [200, 201, 204]:
    print(f"Upload successful: {result['filename']}")
    
    # Step 2: Wait for file to register
    time.sleep(2)
    
    # Step 3: List files to verify
    files = client.get_cloud_files()
    print(f"Found {len(files)} files in cloud")
    
    # Step 4: Start print
    print_result = client.start_cloud_print(
        device_id="01234567890ABCD",
        filename="my_model.3mf"
    )
    
    print(f"Print started! Job ID: {print_result.get('job_id')}")
```

#### File Listing Details

The `get_cloud_files()` method tries multiple endpoints:

1. **Projects endpoint** - Lists projects and their files
2. **Files endpoint** - Direct file listing
3. **Tasks endpoint** - May show files used in print tasks

Returns unified list with:
- `name` / `file_name` / `title` - File name
- `file_id` / `model_id` / `id` - File identifier
- `file_url` / `url` - Download/access URL
- Other metadata (size, date, etc.)

#### Print Job Response

When starting a print, you get:

```python
{
    'job_id': 'job_012345',
    'status': 'queued',  # or 'pending', 'running'
    'device_id': '01234567890ABCD',
    'file_name': 'api_test.3mf',
    'created_at': '2024-01-01T12:00:00Z',
}
```

#### Print Settings

Optional settings you can pass:

```python
settings = {
    'layer_height': 0.2,      # mm
    'infill': 20,             # percent
    'speed': 100,             # percent
    'temperature': 220,       # nozzle temp (C)
    'bed_temperature': 60,    # bed temp (C)
    'support': True,          # enable supports
    'brim': False,            # enable brim
}

client.start_cloud_print(
    device_id="...",
    filename="model.3mf",
    settings=settings
)
```

#### Important Notes

**File Availability:**
- Uploaded files may take 1-2 seconds to appear in listings
- Not all accounts have cloud storage enabled
- Some regions may not support remote printing

**Limitations:**
- Can list uploaded files
- Can start prints from cloud files
- Can pass print settings
- Can get job status
- Can't download files from cloud (no download endpoint)
- Can't delete files (endpoint unknown)
- Can't modify files (must re-upload)
- Can't perform real-time print control (use MQTT for monitoring)

### Cloud Video Streaming

#### Overview

Bambu Lab printers may support video streaming through the cloud when you're not on the local network.

#### Getting Cloud Video URL

```python
from bambulab import BambuClient

client = BambuClient("YOUR_TOKEN")
devices = client.get_devices()
device_id = devices[0]['dev_id']

# Try to get cloud video stream
video_info = client.get_cloud_video_url(device_id)

if 'url' in video_info or 'stream_url' in video_info:
    url = video_info.get('url') or video_info.get('stream_url')
    print(f"Cloud stream URL: {url}")
else:
    # Fall back to local streaming with TTCode
    ttcode = video_info.get('ttcode')
    print("Cloud streaming not available, use local access")
```

#### Availability

- Not all accounts have cloud video enabled
- May require Bambu Lab Cloud subscription
- May be region-specific
- If not available, use local streaming (TUTK or local JPEG/RTSP)

#### Local vs Cloud Streaming

**Local Streaming (Always Available):**
- P1/A1: TLS/TCP port 6000 (JPEG frames)
- X1: RTSP port 322
- Requires being on same network
- No latency
- Higher quality

**Cloud Streaming (If Available):**
- Works from anywhere
- Goes through Bambu servers
- May have latency
- May be lower quality
- Requires cloud subscription

### Upload Troubleshooting

#### S3 Signature Issues

**Error:** `SignatureDoesNotMatch` (403)

This is NOT about certificates or X.509. The issue is with **S3 signed URLs**.

**What S3 Signed URLs Do:**

When you get an upload URL from Bambu's API:
```
https://s3.us-west-2.amazonaws.com/...?AWSAccessKeyId=...&Signature=...&Expires=...
```

AWS S3 pre-calculates a signature based on:
- HTTP method (PUT)
- URL path
- Headers that will be sent
- File content (sometimes)

If ANY of these don't match, you get `SignatureDoesNotMatch`.

**The Fix:**

Use minimal/no extra headers:

```python
response = requests.put(
    upload_url,
    data=file_content,
    headers={},  # Empty - let requests add only what's needed
    timeout=300
)
```

The `requests` library will still add necessary headers like Content-Length automatically, but we're not forcing specific values that might break the signature.

**Why This Happens:**

S3 signed URLs are very strict:
1. Server generates URL with signature
2. Signature is based on exact request parameters
3. If client changes anything, signature fails
4. This includes adding headers server didn't expect

The signed URL IS the authentication. It contains:
- `AWSAccessKeyId` - Identifies the account
- `Signature` - Proves the URL is valid
- `Expires` - URL expiration timestamp

**Other Possible Issues:**

1. **File size mismatch** - Make sure file size in get_upload_url() matches actual file
2. **Expired URL** - Signatures expire (check Expires parameter)
3. **Modified content** - File content must match what was specified
4. **Network proxy** - Proxy might add headers breaking signature

#### Testing Upload Availability

```python
from bambulab import BambuClient

client = BambuClient("YOUR_TOKEN")

# Test if upload is available
try:
    upload_info = client.get_upload_url(filename="test.3mf", size=012345)
    
    if upload_info.get('upload_url') or upload_info.get('urls'):
        print("Cloud upload is available!")
    else:
        print("Cloud upload not available for this account")
        print("Full response:", upload_info)
        
except Exception as e:
    print(f"Error checking upload: {e}")
```

#### Upload Troubleshooting Guide

**Empty upload_info response:**
- Your account may not have cloud storage
- Try verifying your account in Bambu Studio
- Check if cloud features work in Bambu Studio/Handy

**"Cloud upload not available" message:**
- This is expected for some accounts
- Use local FTP upload instead
- Contact Bambu Lab support to enable cloud features

**Upload fails with 403/401:**
- Token may be expired - get a new one
- Account permissions issue
- Try refreshing your session in Bambu Studio

**Upload times out:**
- File may be too large
- Network connection issue
- Cloud service may be unavailable

### Alternative: Local FTP Upload

If cloud upload isn't available, you can upload files directly to the printer via FTP:

```python
from bambulab import LocalFTPClient

# Connect to printer
ftp = LocalFTPClient("012.012.0.012", "01234567")
ftp.connect()

# Upload file
ftp.upload_file("model.3mf", "/model.3mf")

# Print it
from bambulab import LocalPrintClient
printer = LocalPrintClient("012.012.0.012", "01234567")
printer.start_print("/model.3mf")

ftp.disconnect()
```

---


## EXAMPLES

### Complete Request Example

```bash
curl -X GET "https://api.bambulab.com/v1/iot-service/api/user/device/info?device_id=GLOF01234567901" \
  -H "Authorization: Bearer fascvj789VHXDKJVfs7fs9f9..." \
  -H "Content-Type: application/json" \
  -H "x-bbl-app-certification-id: GLOF01234567901:01234567901" \
  -H "x-bbl-device-security-sign: cvhx78xVF78vxhjksdHSjdkjhfksd..."
```

### Python Example

```python
import requests

BASE_URL = "https://api.bambulab.com/v1"
TOKEN = "your_bearer_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "x-bbl-app-certification-id": "your_cert_id",
    "x-bbl-device-security-sign": "your_signature"
}

# Get device info
response = requests.get(
    f"{BASE_URL}/iot-service/api/user/device/info",
    headers=headers,
    params={"device_id": "GLOF01234567901"}
)

print(response.json())
```




---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management and print jobs
- [API_USERS.md](API_USERS.md) - User tasks and projects
- [API_MQTT.md](API_MQTT.md) - MQTT protocol for print control
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
