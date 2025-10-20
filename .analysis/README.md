# API Discovery Methodology

Documentation of how Bambu Lab API endpoints were discovered through analysis of the Bambu Studio application.

---

## Overview

API endpoints were discovered by extracting and analyzing the Bambu Studio/Connect Electron application's router file. This methodology uses pattern matching only - no code deobfuscation or proprietary logic extraction.

---

## Extraction Process

### 1. Extract Application Resources

```bash
# Extract the Windows executable (it's a 7z archive)
7z x BambuStudio.exe -o./bambu_extracted

# Extract the ASAR archive containing the application code
npm install -g asar
asar extract ./bambu_extracted/resources/app.asar ./app_extracted

# Locate the router file (contains API endpoint definitions)
find ./app_extracted -name 'router-*.js' -type f
```

The router file is typically at: `.vite/renderer/main_window/assets/router-[hash].js` (~14MB JavaScript bundle)

### 2. Run Analysis Tool

```bash
python extract_api_from_router.py ./app_extracted/path/to/router-*.js
```

The script performs pattern matching to extract:
- Base URLs (https://api.bambulab.com)
- API endpoint paths (/v1/*, /api/*)
- HTTP methods (GET, POST, PUT, DELETE)
- Custom headers (x-*, Authorization)
- Query parameters

### 3. Test Discovered Endpoints

```bash
# Verify endpoints with your own credentials
cd ../testing
python test_cloud_api.py your.email@example.com
python query_all_printer_info.py YOUR_TOKEN
```

---

## Analysis Tool

### `extract_api_from_router.py`

Pattern matching tool that extracts API structure from the router JavaScript file.

**Usage:**
```bash
python extract_api_from_router.py <router_file.js> [output.json]
python extract_api_from_router.py --help
```

**Extracts:**
- Base URLs and API servers
- Endpoint paths categorized by service
- HTTP methods used
- Authentication headers
- Query parameters

**Output:** JSON file with complete API structure

**Does NOT:**
- Deobfuscate code
- Extract proprietary logic
- Include application source code

### `extract_gcode_profiles.py`

Extracts G-code configuration profiles from router JavaScript and organizes by printer model.

**Usage:**
```bash
python extract_gcode_profiles.py <router_file.js>
```

**Extracts:**
- Machine start/end G-code for each printer model
- Layer change G-code
- Filament change G-code
- Time lapse G-code
- Nozzle-specific configurations

**Output:** 
- `gcode_profiles/` directory with organized G-code files
- `index.json` with printer model catalog
- Metadata files for each printer

**Supported Printers:**
- X1 Carbon, X1, X1E
- P1P, P1S
- A1, A1 mini
- H2D

---

## Discovered API Structure

### Base URLs
```
Production:
  https://api.bambulab.com  (Global)
  https://api.bambulab.cn   (China)

MQTT:
  us.mqtt.bambulab.com:8883 (Global)
  cn.mqtt.bambulab.com:8883 (China)
```

### API Services
- **IoT Service** (`/v1/iot-service/api/`) - Device management, print status
- **User Service** (`/v1/user-service/`) - Authentication, profiles
- **Design Service** (`/v1/design-user/`) - Projects, files, slicer resources

---

## Results

Discovered endpoints are documented in:
- `frontend_api_structure.json` - Raw discovered endpoints
- `docs/API_GUIDE.md` - Complete API reference
- `docs/VERIFIED_ENDPOINTS.md` - Tested endpoints

All analysis outputs are in `.gitignore`.

---

## Ethical & Legal Compliance

This analysis:
- Documents publicly accessible API endpoints
- Enables community integrations and home automation
- Complies with fair use for interoperability
- Uses only your own credentials for testing

Does NOT:
- Bypass security measures
- Violate terms of service
- Redistribute proprietary code
- Enable unauthorized access
