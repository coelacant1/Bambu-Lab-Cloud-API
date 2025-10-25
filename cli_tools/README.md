# Bambu Lab CLI Tools

Command-line utilities for interacting with Bambu Lab 3D printers.

## Tools

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

## Dependencies

```bash
# Core dependencies
pip install requests paho-mqtt

# Optional for camera viewer
pip install opencv-python
```

## Integration

These tools use the `bambulab` library for API and MQTT access. See `../bambulab/README.md` for library documentation.

