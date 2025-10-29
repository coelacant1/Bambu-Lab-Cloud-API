# Bambu Lab CLI Tools

Command-line utilities for interacting with Bambu Lab 3D printers.

## Tools

### login.py - Authentication & Token Management

Authenticate with Bambu Lab and save your access token locally. Supports email verification (2FA) and multi-factor authentication.

**Usage:**
```bash
# Interactive login (prompts for email/password)
python login.py

# Login with credentials
python login.py --username user@email.com --password mypassword

# Use China region
python login.py --region china

# Custom token file location
python login.py --token-file ~/.my_bambu_token

# Verify existing token
python login.py --verify-only

# Force new login (ignore existing token)
python login.py --force
```

**Features:**
- Interactive email/password prompts
- Email verification code (2FA) support
- Automatic token saving to `~/.bambu_token`
- Token validation and testing
- Regional support (Global/China)
- Secure token file permissions (0600)

**Examples:**
```bash
# First time login (interactive)
python login.py
# Prompts for email, password, and verification code

# Login for China region
python login.py --region china

# Verify your saved token still works
python login.py --verify-only

# Force re-authentication
python login.py --force --username user@email.com
```

**Token Storage:**
- Default location: `~/.bambu_token`
- File permissions: `0600` (user read/write only)
- Used automatically by other CLI tools

---

### monitor.py - Real-time MQTT Monitoring

Monitor your printer in real-time with formatted output showing temperatures, progress, and more.

**Usage:**
```bash
python monitor.py <username> <token> <device_id>
```

**Features:**
- Real-time temperature monitoring (nozzle, bed, chamber)
- Print progress and ETA
- Fan speeds
- Layer information
- Formatted, color-coded output

**Example:**
```bash
python monitor.py u_1234567890 bbl-token-abc123 01P00A123456789
```

### query.py - Printer Information Query

Query printer information from the Bambu Lab Cloud API.

**Usage:**
```bash
python query.py <token> [options]
```

**Options:**
- `--devices` - Show device list
- `--status` - Show print status for all devices
- `--profile` - Show user profile information
- `--projects` - Show user projects
- `--firmware` - Show firmware information
- `--json` - Output in JSON format (default: human-readable)

**Examples:**
```bash
# Show all devices
python query.py bbl-token-abc123 --devices

# Show device status
python query.py bbl-token-abc123 --status

# Get everything in JSON format
python query.py bbl-token-abc123 --devices --status --projects --json
```

### camera_viewer.py - Live Camera Feed

View live camera feed from your Bambu Lab printer. Supports both JPEG streams (P1/A1 series) and RTSP streams (X1 series).

**Usage:**
```bash
python camera_viewer.py <token> [options]
```

**Options:**
- `--ip <address>` - Printer IP address (auto-detected if omitted)
- `--access-code <code>` - Printer access code (from query.py)
- `--device-id <serial>` - Device serial number
- `--save` - Save frames to disk
- `--output-dir <path>` - Directory for saved frames (default: frames/)
- `--max-frames <n>` - Stop after N frames
- `--list` - List available printers

**Examples:**
```bash
# Auto-detect printer and view stream
python camera_viewer.py bbl-token-abc123

# Specify printer by IP
python camera_viewer.py bbl-token-abc123 --ip 192.168.1.100 --access-code 12345678

# Save frames to disk
python camera_viewer.py bbl-token-abc123 --save --output-dir snapshots/

# Save 100 frames then exit
python camera_viewer.py bbl-token-abc123 --save --max-frames 100

# List available printers
python camera_viewer.py bbl-token-abc123 --list
```

**Features:**
- **P1/A1 Series**: JPEG frame streaming with OpenCV display
- **X1 Series**: RTSP URL generation with viewing instructions
- Real-time FPS counter overlay
- Frame saving capability
- Auto-detection of printer model and IP
- Interactive printer selection

**Requirements:**
```bash
pip install opencv-python  # For viewing JPEG streams
# VLC or ffmpeg for RTSP streams (X1 series)
```

## Quick Start

1. **Authenticate first:**
   ```bash
   python login.py
   # Follow prompts to enter email, password, and verification code
   ```

2. **Query your devices:**
   ```bash
   python query.py $(cat ~/.bambu_token) --devices
   ```

3. **Monitor in real-time:**
   ```bash
   python monitor.py USERNAME $(cat ~/.bambu_token) DEVICE_ID
   ```

4. **View camera feed:**
   ```bash
   python camera_viewer.py $(cat ~/.bambu_token)
   ```

## Dependencies

All tools require the base package:
```bash
pip install bambu-lab-cloud-api
```

Individual tool dependencies:
```bash
# For monitor.py and query.py (included in base)
pip install requests paho-mqtt

# For camera_viewer.py (included in base)
pip install opencv-python

# For login.py (included in base)
# No additional dependencies needed
```

## Tool Comparison

| Tool | Purpose | Requires Token | Requires Device ID | Interactive |
|------|---------|----------------|-------------------|-------------|
| **login.py** | Get token | No | No | Yes |
| **query.py** | Get device info | Yes | No | No |
| **monitor.py** | Live MQTT data | Yes | Yes | Yes |
| **camera_viewer.py** | Camera feed | Yes | Optional | Yes |

## Workflow

```
1. login.py          → Get and save token
2. query.py          → Find device IDs and info
3. monitor.py        → Watch printer in real-time
   OR
   camera_viewer.py  → View camera feed
```

## Integration

These tools use the `bambulab` library for API and MQTT access. See `../bambulab/README.md` for library documentation.

