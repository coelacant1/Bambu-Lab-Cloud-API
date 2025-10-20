# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-10-22

### Added
- **Python Library** (`bambulab/`) - Unified client library for Cloud API, MQTT, FTP, and video streaming
  - `BambuClient` - Cloud API client with authentication
  - `MQTTClient` - Real-time printer monitoring
  - `LocalFTPClient` - File upload via FTP
  - `JPEGFrameStream` / `RTSPStream` - Video streaming support
- **Compatibility Layer** (`servers/compatibility.py`) - Bridges legacy local API to Cloud API without developer mode
- **Proxy Servers** (`servers/proxy.py`) - Strict read-only and full proxy modes with custom authentication
- **CLI Tools** (`cli_tools/`) - Query and monitoring utilities
- **Comprehensive Testing** (`tests/`) - Unit tests for all library components
- **Complete Documentation** (`.docs/CLOUD_API.md`) - API reference with Python, JavaScript, and cURL examples

### Changed
- Restructured project into library-first architecture
- Enhanced multi-device and multi-printer support
- Improved authentication with token management

## [1.0.0] - 2025-10-18

### Initial Release
- Cloud API HTTP endpoint documentation
- MQTT protocol implementation and documentation
- FTP and video streaming protocol documentation
- G-code command reference
- Authentication methods (email/password, verification code)
- Working read operations for devices, status, projects, user data
- Basic examples and testing tools

### Verified Functionality
- Cloud API: devices, firmware, status, projects, user profile, tasks, messages, preferences
- MQTT: real-time monitoring, temperature, fan speed, print progress, AMS status
- Authentication: login, token refresh, expiration handling

### Known Limitations
- Some endpoints require specific parameters
- MQTT topics vary by printer model
- Token expires after ~90 days
- Write operations minimally tested for safety
- Video streaming and file uploads in progress

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

