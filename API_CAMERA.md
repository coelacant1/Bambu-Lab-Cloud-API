# Bambu Lab Cloud API - Camera & Video Streaming

**Last Updated:** 2025-10-25

This document covers camera credentials, TUTK P2P protocol, video streaming, and local JPEG access.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

---

### Camera & Video Streaming

#### Overview

Bambu Lab printers support camera streaming using two methods:
1. **TUTK P2P Protocol** - Remote access via proprietary P2P (used by Bambu Studio/Handy)
2. **Local JPEG Stream** - Direct TCP connection on same network (higher quality, lower latency)

#### Get Camera Credentials (TTCode)

```http
POST /v1/iot-service/api/user/ttcode
Content-Type: application/json

Request Body:
{
  "dev_id": "01234567890ABCD"
}

Response:
{
  "message": "success",
  "code": null,
  "error": null,
  "ttcode": "01234567890ABCDEF012",
  "authkey": "01234567",
  "passwd": "012345",
  "region": "us",
  "type": "tutk",
  "streams": null,
  "peers": null,
  "stream_key": "",
  "stream_salt": "",
  "channel_name": "",
  "app_id": "",
  "rtm": null
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `ttcode` | TUTK P2P UID for camera connection |
| `authkey` | Authentication key for TUTK protocol |
| `passwd` | Camera access password (6-character hex) |
| `type` | Protocol type (`tutk` for P2P) |
| `region` | Server region (`us` or `cn`) |
| `stream_key` | Reserved for future cloud streaming |
| `stream_salt` | Reserved for future cloud streaming |
| `channel_name` | Reserved for future cloud streaming |
| `app_id` | Reserved for future cloud streaming |
| `rtm` | Real-time messaging config (unused) |
| `streams` | Reserved (null) |
| `peers` | Reserved (null) |

#### What is TUTK?

**TUTK (Throughtek UDP Tunnel Kit)** is a peer-to-peer video streaming protocol:
- Proprietary P2P protocol (not HTTP/RTSP)
- Works through firewalls/NAT without port forwarding
- Used by Bambu Studio and Bambu Handy for remote camera access
- Requires TUTK SDK (not open source)
- Lower latency than cloud-based streaming
- Reduced server costs for Bambu Lab

TUTK is a P2P protocol, not HTTP/RTSP, so:
- Can't use VLC/ffmpeg with a simple URL
- No direct HTTPS streaming endpoint
- Not compatible with standard video players
- Lower latency (peer-to-peer)
- Works through NAT/firewalls
- Built into Bambu Studio/Handy

#### Camera Streaming Methods

**1. Remote TUTK P2P Streaming** (Works Anywhere)

Uses the TTCode credentials from the API:

```python
# Get TUTK credentials
ttcode_data = client.get_ttcode("01234567890ABCD")

# TUTK connection parameters:
# - UID: ttcode_data['ttcode']        # Example: 01234567890ABCDEF012
# - Auth Key: ttcode_data['authkey']  # Example: 01234567
# - Password: ttcode_data['passwd']   # Example: 012345

# Requires TUTK SDK (proprietary, not included in this library)
# Best used through Bambu Studio or Bambu Handy apps
```

**Viewing via TUTK:**
1. Open Bambu Studio or Bambu Handy
2. Select your printer
3. View live camera feed
4. Works from anywhere (not limited to local network)

**2. Local JPEG Stream** (Same Network Only)

Direct TCP connection for higher quality and lower latency:

```python
from bambulab import JPEGFrameStream

# Connect to printer on local network
stream = JPEGFrameStream(
    ip="012.012.0.012",
    access_code="01234567",  # 8-digit access code from printer
    model="P1S"  # or "X1C", "A1", etc.
)

# Connect
stream.connect()

# Get frames
while True:
    frame = stream.get_frame()  # Returns PIL Image
    if frame:
        # Display or save frame
        frame.show()  # or frame.save('snapshot.jpg')
    time.sleep(0.1)

stream.disconnect()
```

**Local Stream Details:**
- Protocol: TLS over TCP
- Port: 6000 (P1/A1 models)
- Format: JPEG frames
- Resolution: 1920x1080 or 1280x720
- Frame Rate: ~10-30 FPS (varies by model)
- Requires: 8-digit access code from printer screen

**Camera Viewer CLI Tool:**

```bash
cd cli_tools
python camera_viewer.py --ip 012.012.0.012 --code 01234567 --model P1S
```

Displays live camera feed in a window.

#### Cloud Streaming Status

**Current Status:** Not Available

The API response includes empty fields for cloud streaming:
- `streams` = null
- `stream_key` = ""
- `channel_name` = ""
- `app_id` = ""

These fields are reserved for future cloud streaming features (likely WebRTC-based) but are not currently implemented.

#### Local vs Remote Comparison

| Feature | Local JPEG | TUTK P2P | Cloud (N/A) |
|---------|-----------|----------|-------------|
| **Network** | Same LAN only | Anywhere | Anywhere |
| **Quality** | High (1080p) | Medium | Unknown |
| **Latency** | Very Low | Low | High |
| **Setup** | Access code | TTCode API | N/A |
| **Tools** | JPEGFrameStream | Bambu Studio | N/A |
| **SDK Required** | No | Yes | N/A |

#### Python Examples

**Example 1: Get TTCode Credentials**

```python
from bambulab import BambuClient

client = BambuClient("YOUR_TOKEN")

# Get camera credentials for remote access
ttcode = client.get_ttcode("01234567890ABCD")

print(f"TUTK UID: {ttcode['ttcode']}")
print(f"Auth Key: {ttcode['authkey']}")
print(f"Password: {ttcode['passwd']}")
print(f"Region: {ttcode['region']}")

# These credentials work with:
# - Bambu Studio (built-in TUTK support)
# - Bambu Handy (mobile app)
# - Custom apps using TUTK SDK
```

**Example 2: Local Camera Streaming**

```python
from bambulab import JPEGFrameStream
import cv2
import numpy as np

# Connect to local camera
stream = JPEGFrameStream("012.012.0.012", "01234567", model="P1S")
stream.connect()

try:
    while True:
        # Get frame as PIL Image
        pil_frame = stream.get_frame()
        
        if pil_frame:
            # Convert to OpenCV format for processing
            frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
            
            # Display
            cv2.imshow('Bambu Camera', frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    stream.disconnect()
    cv2.destroyAllWindows()
```

**Example 3: Save Snapshots**

```python
from bambulab import JPEGFrameStream
from datetime import datetime

stream = JPEGFrameStream("012.012.0.012", "01234567", model="P1S")
stream.connect()

# Take a snapshot
frame = stream.get_frame()
if frame:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame.save(f"snapshot_{timestamp}.jpg")
    print(f"Snapshot saved: snapshot_{timestamp}.jpg")

stream.disconnect()
```

**Example 4: Monitor Print via Camera**

```python
from bambulab import JPEGFrameStream, MQTTClient
import time

# Setup MQTT for print status
mqtt = MQTTClient(
    username="bblp",
    token="your_token",
    device_id="01234567890ABCD"
)

# Setup camera
camera = JPEGFrameStream("012.012.0.012", "01234567", model="P1S")

# Connect both
mqtt.connect()
camera.connect()

# Monitor printing
def on_status(data):
    if 'print' in data:
        progress = data['print'].get('mc_percent', 0)
        if progress > 0:
            # Take snapshot at progress milestones
            if progress % 10 == 0:
                frame = camera.get_frame()
                if frame:
                    frame.save(f"print_progress_{progress}pct.jpg")
                    print(f"Snapshot at {progress}%")

mqtt.subscribe_to_updates(on_status)

try:
    while True:
        time.sleep(1)
finally:
    mqtt.disconnect()
    camera.disconnect()
```

#### Camera Access Requirements

**For Local JPEG Stream:**
- Printer IP address (same network)
- 8-digit access code (from printer screen settings)
- Printer model (P1S, X1C, A1, etc.)

**For TUTK P2P Stream:**
- Bambu Lab Cloud account token
- Device serial number
- Bambu Studio or Bambu Handy app (easiest)
- OR TUTK SDK for custom apps (proprietary)

#### Troubleshooting

**Local Stream Issues:**
- **Connection refused:** Check IP address and network
- **Authentication failed:** Verify 8-digit access code
- **Timeout:** Ensure firewall allows port 6000
- **No frames:** Camera might be disabled in printer settings

**TUTK Issues:**
- **TTCode not working:** Token may be expired, get new one
- **Cannot connect from remote:** Firewall blocking UDP P2P
- **No video in app:** Camera may be disabled on printer

**General:**
- **Black screen:** Check printer camera settings
- **Low FPS:** Network congestion or weak signal
- **Choppy video:** Use local stream instead of TUTK for better quality

---


---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management
- [API_MQTT.md](API_MQTT.md) - MQTT protocol
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
