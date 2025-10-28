# Changelog

All notable changes to this project will be documented in this file.

## [1.0.3]

### Added
- **Two-Factor Authentication Support**
  - `BambuAuthenticator` class for complete login flow with 2FA
  - Automatic email verification code handling
  - MFA (multi-factor authentication) support
  - Token persistence with secure file storage (0600 permissions)
  - Token validation and auto-refresh functionality
  - Support for both Global and China API regions
- **CLI Authentication Tool** (`cli_tools/login.py`)
  - Interactive login with email verification code prompt
  - Non-interactive mode with command-line arguments
  - Token verification and testing
  - Force new login option
- **Authentication Documentation**
  - Updated [API_AUTHENTICATION.md](API_AUTHENTICATION.md) with complete login flow
- **Authentication Tests**
  - Unit tests for `BambuAuthenticator` class
  - Token save/load/verify functionality tests
  - Mock-based login flow testing
  - 12/12 tests passing

### Changed
- Enhanced `bambulab/__init__.py` to export `BambuAuthenticator` and `BambuAuthError`
- Updated README.md with authentication quick start guide
- Improved auth.py with comprehensive 2FA flow implementation

## [1.0.0] - 2025-10-25

### Major Release
This release provides a comprehensive, library and documentation for interacting with Bambu Lab printers via cloud and local protocols without requiring developer mode.

### Added
- **Complete Python Library** (`bambulab/`)
  - `BambuClient` - Full Cloud API implementation with authentication, token management, and auto-refresh
  - `MQTTClient` - Real-time MQTT monitoring with comprehensive message parsing
  - `LocalFTPClient` - Secure FTP file upload for local network operations
  - `JPEGFrameStream` / `RTSPStream` - Video streaming support for camera integration
- **Comprehensive Documentation**
  - API reference split into logical modules: Authentication, Devices, Users, Files/Printing, AMS/Filament, Camera, MQTT
  - Python, JavaScript, and cURL examples for all endpoints
  - Complete response schemas with actual field documentation
  - G-code and MQTT command references
- **Testing Suite** (`tests/`)
  - Comprehensive test coverage for all API endpoints
  - MQTT stream monitoring and validation
  - File upload testing with cloud and local FTP
  - Camera stream integration tests
  - Detailed output of all API responses for verification
- **CLI Tools** (`cli_tools/`)
  - Device query and management utilities
  - Real-time MQTT monitoring tools
  - File upload helpers
- **Server Components** (`servers/`)
  - Compatibility layer bridging legacy local API to cloud API
  - Proxy servers with read-only and full access modes
  - Custom authentication support

### Documentation
- All API endpoints fully documented with request/response examples
- MQTT message structure and topic documentation
- Camera streaming protocols (TUTK/RTSP/JPEG)
- FTP upload procedures for local and cloud
- Authentication flows with token lifecycle management

### Verified Functionality
- Cloud API: 40+ endpoints across devices, users, projects, tasks, messages, preferences, filaments
- MQTT: Real-time status, temperatures, fan speeds, print progress, AMS status, HMS error codes
- File Operations: Cloud upload, local FTP, project management
- Camera: TTCode retrieval, local JPEG/RTSP streaming
- Authentication: Email/password, verification codes, token refresh, multi-device support

---

## [0.3.0] - 2025-10-18

### Added
- CLI tools for device queries
- Proxy server implementation
- Local FTP client integration
- Enhanced MQTT message parsing

### Fixed
- Token refresh timing issues
- MQTT reconnection handling
- File upload content-type headers

---

## [0.2.2] - 2025-10-15

### Added
- Video streaming documentation
- Camera TTCode endpoint integration
- JPEG frame extraction utilities

### Changed
- Improved error handling for API requests
- Enhanced logging throughout library

---

## [0.2.1] - 2025-10-13

### Fixed
- MQTT connection stability
- Authentication token expiration edge cases
- Multi-device selection logic

### Added
- Comprehensive test suite foundation

---

## [0.2.0] - 2025-10-11

### Added
- MQTT client implementation
- Real-time printer monitoring
- AMS filament status tracking
- G-code command reference

### Changed
- Refactored authentication module
- Consolidated API base URLs

---

## [0.1.3] - 2025-10-09

### Added
- Project listing and management endpoints
- Task history retrieval
- Message and notification APIs

### Fixed
- Response parsing for nested structures

---

## [0.1.2] - 2025-10-07

### Added
- User profile endpoints
- Device firmware information
- Print status monitoring

### Changed
- Improved response field documentation

---

## [0.1.1] - 2025-10-06

### Fixed
- Authentication header formatting
- Device listing pagination
- Error response handling

### Added
- Basic examples for common operations

---

## [0.1.0] - 2025-10-04

### Initial Development Release
- Core authentication implementation
- Basic device listing
- HTTP client foundation
- Initial API endpoint discovery

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

