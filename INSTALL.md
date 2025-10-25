# Installation Guide

## Quick Install

### From PyPI (Recommended)

```bash
# Basic installation
pip install bambu-lab-cloud-api

# With server components
pip install bambu-lab-cloud-api[server]

# With development tools
pip install bambu-lab-cloud-api[dev]

# Everything
pip install bambu-lab-cloud-api[all]
```

### From GitHub (Latest)

```bash
# Install directly from GitHub main branch
pip install git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git

# With extras
pip install "bambu-lab-cloud-api[server] @ git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git"
pip install "bambu-lab-cloud-api[all] @ git+https://github.com/coelacant1/Bambu-Lab-Cloud-API.git"
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/coelacant1/Bambu-Lab-Cloud-API.git
cd Bambu-Lab-Cloud-API

# Install in development mode
pip install -e .

# Or install with server dependencies
pip install -e ".[server]"

# Or install with all dependencies
pip install -e ".[all]"
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

### Core Dependencies
- `requests>=2.25.0` - HTTP API calls
- `paho-mqtt>=1.6.0` - MQTT communication

### Server Dependencies (optional)
- `flask>=2.0.0` - Web server framework
- `flask-cors>=3.0.0` - CORS support

### Development Dependencies (optional)
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting

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
