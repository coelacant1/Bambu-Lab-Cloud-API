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

## Dependencies

```bash
pip install requests paho-mqtt
```

## Integration

These tools use the `bambulab` library for API and MQTT access. See `../bambulab/README.md` for library documentation.

