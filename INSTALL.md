# Installation Guide

## Quick Install

### From PyPI (Recommended)

```bash
# Complete installation (includes all features)
pip install bambu-lab-cloud-api

# With development tools only
pip install bambu-lab-cloud-api[dev]
```

**Note:** As of v1.0.4, the base install includes all features (API, MQTT, camera, proxy server).
No need for `[server]` or `[all]` extras anymore!

### From GitHub (Latest)

```bash
# Install directly from GitHub main branch
pip install git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/coelacant1/Bambu-Lab-Cloud-API.git
cd Bambu-Lab-Cloud-API

# Install in development mode
pip install -e .

# Or with development tools
pip install -e ".[dev]"
```

## Configuration

### For Testing

```bash
cd tests
cp test_config.json.example test_config.json
# Edit test_config.json with your credentials
```

### For Proxy Server

```bash
cd servers
cp proxy_tokens.json.example proxy_tokens.json
# Edit proxy_tokens.json with your token mappings
```

### For Compatibility Layer

```bash
cd servers
cp compatibility_config.json.example compatibility_config.json
# Edit compatibility_config.json with your credentials
```

## Verify Installation

```bash
# Test the library
python -c "from bambulab import BambuClient; print('Success!')"

# Run comprehensive tests
cd tests
python test_comprehensive.py
```

## CLI Tools

After installation, you can use the command-line tools:

```bash
# Query printer status
bambu-query --help

# Monitor printer in real-time
bambu-monitor --help

# View camera feed
bambu-camera --help
```

## Dependencies

### Included in Base Install

- `requests>=2.25.0` - HTTP API calls
- `paho-mqtt>=1.6.0` - MQTT communication
- `opencv-python>=4.0.0` - Camera streaming
- `flask>=2.0.0` - Proxy server
- `flask-cors>=3.0.0` - CORS support
- `flask-limiter>=3.5.0` - Rate limiting

### Optional: Development Tools

- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting

Install with: `pip install bambu-lab-cloud-api[dev]`

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:
```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Permission Errors

On Linux/Mac, you may need to use `pip3` instead of `pip`:
```bash
pip3 install -e .
```
