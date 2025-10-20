# Bambu Lab Proxy and Compatibility Servers

Servers for Bambu Lab Cloud API integration

## Servers

### proxy.py - API Proxy Server

A unified proxy with multiple modes for different use cases.

**Modes:**
- **strict** - Only GET requests allowed (port 5001)
- **full** - Complete 1:1 proxy with all operations (port 5003)

**Usage:**
```bash
# Run in strict mode (read-only)
python proxy.py strict

# Run in full mode (all operations)
python proxy.py full
```

**Features:**
- Token-based authentication with custom token mapping
- Multiple operation modes for security
- Health monitoring endpoints
- CORS support
- Request logging

**Configuration:**

Create `proxy_tokens.json` for custom token mapping:
```json
{
  "custom-token-1": "real-bambu-token-xyz",
  "custom-token-2": "real-bambu-token-abc"
}
```

See `../proxy/README.md` for detailed configuration.

### compatibility.py - Legacy API Compatibility Layer

Provides backward compatibility for legacy tools and home automation systems that relied on the old local API access.

**Usage:**
```bash
python compatibility.py
```

**Features:**
- Mimics old local API endpoints
- Translates requests to Cloud API
- MQTT bridge for real-time updates
- Works without developer mode
- Compatible with Home Assistant, Octoprint, and other legacy integrations

**Configuration:**

Create `compatibility_config.json`:
```json
{
  "devices": [
    {
      "serial": "01P00A123456789",
      "access_code": "12345678",
      "name": "My Printer"
    }
  ],
  "username": "u_1234567890",
  "auth_token": "your-bambu-token"
}
```

See `../compatibility/README.md` for detailed configuration.

## Port Mapping

| Server | Mode | Port | Purpose |
|--------|------|------|---------|
| proxy.py | strict | 5001 | Read-only API access |
| proxy.py | full | 5003 | Full API access |
| compatibility.py | - | 8080 | Legacy API compatibility |

## Dependencies

```bash
pip install requests paho-mqtt flask flask-cors
```

## Integration

These servers use the `bambulab` library for API and MQTT access. See `../bambulab/README.md` for library documentation.

## Running Servers

### Using systemd (Linux)

Create service files for each server:

**proxy-strict.service:**
```ini
[Unit]
Description=Bambu Lab API Proxy (Strict Mode)
After=network.target

[Service]
Type=simple
User=bambulab
WorkingDirectory=/opt/bambulab/tools/servers
ExecStart=/usr/bin/python3 proxy.py strict
Restart=always

[Install]
WantedBy=multi-user.target
```

**compatibility.service:**
```ini
[Unit]
Description=Bambu Lab Compatibility Layer
After=network.target

[Service]
Type=simple
User=bambulab
WorkingDirectory=/opt/bambulab/tools/servers
ExecStart=/usr/bin/python3 compatibility.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable proxy-strict.service compatibility.service
sudo systemctl start proxy-strict.service compatibility.service
```

