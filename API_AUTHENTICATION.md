# Bambu Lab Cloud API - Authentication

**Last Updated:** 2025-10-28

This document covers all authentication methods for the Bambu Lab Cloud API, including the new login flow with two-factor authentication.

---

## Quick Start: Login with 2FA

### Using the CLI Tool

```bash
# Interactive login (recommended)
python cli_tools/login.py

# Non-interactive login
python cli_tools/login.py --username user@email.com --password yourpass

# China region
python cli_tools/login.py --region china --username user@email.com

# Verify existing token
python cli_tools/login.py --verify-only

# Test token by fetching profile
python cli_tools/login.py --test
```

### Using the Python API

```python
from bambulab import BambuAuthenticator, BambuClient

# Authenticate and get token
auth = BambuAuthenticator(region="global")
token = auth.login(
    username="your-email@example.com",
    password="your-password"
)

# Token is automatically saved to ~/.bambu_token
# Use with API client
client = BambuClient(token=token)
devices = client.get_devices()
```

---

## Login Flow with Two-Factor Authentication

Bambu Lab enforces two-factor authentication via email verification for all users.

### Authentication Process

1. **Initial Login**: Submit email and password
2. **Verification Code**: Bambu Lab sends 6-digit code to your email
3. **Code Verification**: Enter code to complete authentication
4. **Token Received**: Get access token for API calls

### Python Implementation

```python
from bambulab import BambuAuthenticator, BambuAuthError

auth = BambuAuthenticator()

try:
    # Method 1: Interactive (prompts for code)
    token = auth.login("user@email.com", "password")
    
    # Method 2: Custom callback
    def get_code():
        return input("Enter code from email: ")
    
    token = auth.login("user@email.com", "password", get_code)
    
    # Method 3: Use saved token if valid, login if needed
    token = auth.get_or_create_token(
        username="user@email.com",
        password="password"
    )
    
    print(f"Logged in! Token: {token[:20]}...")
    
except BambuAuthError as e:
    print(f"Authentication failed: {e}")
```

### Token Storage

Tokens are automatically saved to `~/.bambu_token` with secure permissions (0600):

```python
{
  "region": "global",
  "token": "eyJhbGc..."
}
```

Custom token file location:

```python
auth = BambuAuthenticator(token_file="/path/to/token.json")
```

---

## Login API Endpoints

### 1. Initial Login

**Endpoint:** `POST /v1/user-service/user/login`

**Request:**
```json
{
  "account": "user@email.com",
  "password": "your_password",
  "apiError": ""
}
```

**Response (Success):**
```json
{
  "success": true,
  "accessToken": "eyJhbGc..."
}
```

**Response (2FA Required):**
```json
{
  "success": false,
  "loginType": "verifyCode"
}
```

**Response (MFA Required):**
```json
{
  "success": false,
  "loginType": "tfa",
  "tfaKey": "..."
}
```

### 2. Send Verification Code

**Endpoint:** `POST /v1/user-service/user/sendemail/code`

**Request:**
```json
{
  "email": "user@email.com",
  "type": "codeLogin"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification code sent"
}
```

### 3. Verify Code and Login

**Endpoint:** `POST /v1/user-service/user/login`

**Request:**
```json
{
  "account": "user@email.com",
  "code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "accessToken": "eyJhbGc..."
}
```

### 4. MFA Verification (if enabled)

**Endpoint:** `POST /api/sign-in/tfa`

**Request:**
```json
{
  "tfaKey": "...",
  "tfaCode": "123456"
}
```

---

## BambuAuthenticator API Reference

### Class: `BambuAuthenticator`

```python
class BambuAuthenticator:
    def __init__(
        self,
        region: str = "global",
        token_file: Optional[str] = None
    )
```

**Parameters:**
- `region`: API region - "global" (default) or "china"
- `token_file`: Path to save tokens (default: `~/.bambu_token`)

### Methods

#### `login()`

Perform login with 2FA support.

```python
def login(
    self,
    username: str,
    password: str,
    code_callback: Optional[Callable[[], str]] = None
) -> str
```

**Parameters:**
- `username`: Bambu Lab account email
- `password`: Account password
- `code_callback`: Optional function to get verification code

**Returns:** Access token string

**Raises:** `BambuAuthError` on failure

#### `get_or_create_token()`

Get existing token or login if needed.

```python
def get_or_create_token(
    self,
    username: Optional[str] = None,
    password: Optional[str] = None,
    code_callback: Optional[Callable[[], str]] = None,
    force_new: bool = False
) -> str
```

**Parameters:**
- `username`: Account email (required if no saved token)
- `password`: Account password (required if no saved token)
- `code_callback`: Optional code input function
- `force_new`: Force new login even if token exists

**Returns:** Valid access token

#### `save_token()`

Save token to file.

```python
def save_token(self, token: str) -> None
```

#### `load_token()`

Load saved token from file.

```python
def load_token(self) -> Optional[str]
```

**Returns:** Token string or None

#### `verify_token()`

Check if token is valid.

```python
def verify_token(self, token: str) -> bool
```

**Returns:** True if valid, False otherwise

---

## Advanced Examples

### Automated Code Retrieval

```python
def fetch_code_from_email():
    """Fetch code from email automatically"""
    # Example: Use IMAP to read email
    import imaplib
    import re
    
    # Connect to email
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('user@email.com', 'app_password')
    mail.select('INBOX')
    
    # Search for Bambu Lab email
    _, messages = mail.search(None, 'FROM "noreply@bambulab.com"')
    latest = messages[0].split()[-1]
    
    # Fetch and parse
    _, msg = mail.fetch(latest, '(RFC822)')
    email_body = msg[0][1].decode()
    
    # Extract 6-digit code
    match = re.search(r'\b\d{6}\b', email_body)
    return match.group(0) if match else None

# Use with authenticator
auth = BambuAuthenticator()
token = auth.login("user@email.com", "password", fetch_code_from_email)
```

### GUI Integration

```python
import tkinter as tk
from tkinter import messagebox

def get_code_via_gui():
    """Show GUI dialog for code input"""
    root = tk.Tk()
    root.withdraw()
    
    code = tk.simpledialog.askstring(
        "Verification Code",
        "Enter the 6-digit code from your email:"
    )
    
    return code

auth = BambuAuthenticator()
token = auth.login("user@email.com", "password", get_code_via_gui)
```

### Retry Logic

```python
from bambulab import BambuAuthenticator, BambuAuthError
import time

def login_with_retry(username, password, max_retries=3):
    """Login with retry logic"""
    auth = BambuAuthenticator()
    
    for attempt in range(max_retries):
        try:
            token = auth.login(username, password)
            return token
        except BambuAuthError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise
    
    return None

token = login_with_retry("user@email.com", "password")
```

---

## Base URLs

### Production APIs

**Global (International):**
```
Main API:    https://api.bambulab.com
Portal:      https://e.bambulab.com
```

**China Region:**
```
Main API:    https://api.bambulab.cn
Portal:      https://e.bambulab.cn
```

### Development/Testing APIs (Internal)

```
Dev API:      https://api-dev.bambulab.net
QA API:       https://api-qa.bambulab.net  
Pre-prod:     https://api-pre.bambulab.net
```

---

## Authentication Headers

All authenticated API requests require these headers:

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
x-bbl-app-certification-id: <cert_id>
x-bbl-device-security-sign: <signed_timestamp>
```

### Header Descriptions

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token obtained from login |
| `Content-Type` | Yes | Always `application/json` for API requests |
| `x-bbl-app-certification-id` | Optional | Device certificate ID for enhanced security |
| `x-bbl-device-security-sign` | Optional | RSA signature of current timestamp |

---

## Certificate-Based Authentication

The Bambu Connect app uses RSA certificate-based signing for enhanced security:

### Process

1. App has a device certificate with RSA key pair
2. Signs current timestamp with private key
3. Sends signature in `x-bbl-device-security-sign` header
4. Sends certificate ID in `x-bbl-app-certification-id` header
5. Server verifies signature with public key from certificate

### Certificate Format

- **Algorithm:** RSA 2048-bit or higher
- **Signature Algorithm:** SHA-256
- **Certificate Storage:** Secure local storage in app

### Python Example (Simplified)

```python
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def sign_timestamp(private_key_pem):
    timestamp = str(int(time.time() * 1000))
    
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    
    # Sign timestamp
    signature = private_key.sign(
        timestamp.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    # Return base64 encoded signature
    import base64
    return base64.b64encode(signature).decode()

# Usage
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-bbl-app-certification-id": cert_id,
    "x-bbl-device-security-sign": sign_timestamp(private_key)
}
```

---

## JWT Token Format

Bambu Lab uses JWT (JSON Web Tokens) for authentication.

### Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "012345678",
    "email": "0123@01234567890",
    "permissions": ["device:read", "device:write", "files:upload"],
    "exp": 1761435401,
    "iat": 1761349001
  },
  "signature": "..."
}
```

### Token Properties

- **Algorithm:** RS256 (RSA with SHA-256)
- **Expiration:** Typically 24 hours
- **Refresh:** Must obtain new token after expiration
- **Scope:** Contains user_id and permissions

### Obtaining a Token

**Note:** The login endpoint is not publicly documented. You must obtain a token through:
1. Official Bambu Connect app
2. Bambu Handy mobile app
3. Web portal login flow

### Token Usage

```python
import requests

headers = {
    "Authorization": f"Bearer {your_token}",
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.bambulab.com/v1/iot-service/api/user/bind",
    headers=headers
)
```

---

## Security Best Practices

### Token Storage

- Store tokens securely (encrypted storage, keychain, etc.)
- Never commit tokens to version control
- Use environment variables for development
- Implement token refresh before expiration

### Certificate Management

- Keep private keys secure and never expose them
- Rotate certificates periodically
- Use hardware security modules (HSM) for production
- Implement certificate revocation checking

### Network Security

- Always use HTTPS
- Validate SSL certificates
- Implement certificate pinning for production apps
- Use secure network connections (avoid public WiFi)

### Error Handling

```python
def make_authenticated_request(url, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 401:
            print("Authentication failed - token expired or invalid")
            # Implement token refresh logic here
            return None
            
        elif response.status_code == 403:
            print("Access forbidden - insufficient permissions")
            return None
            
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
```

---

## Common Authentication Errors

### 401 Unauthorized

**Causes:**
- Expired token
- Invalid token
- Missing Authorization header
- Malformed Bearer token

**Solution:**
- Obtain a new token
- Verify token format: `Bearer <token>`
- Check token expiration time

### 403 Forbidden

**Causes:**
- Insufficient permissions
- Token valid but user lacks access
- Device not bound to user account

**Solution:**
- Verify user permissions
- Ensure device is bound to your account
- Check if feature requires premium subscription

### 400 Bad Request

**Causes:**
- Missing required headers
- Invalid certificate signature
- Malformed request

**Solution:**
- Verify all required headers are present
- Check certificate signing implementation
- Validate request body format

---

## Python Authentication Example

Complete example showing authentication workflow:

```python
import requests
import os

class BambuAuth:
    def __init__(self, token, region="global"):
        self.token = token
        self.base_url = (
            "https://api.bambulab.com" if region == "global"
            else "https://api.bambulab.cn"
        )
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_auth(self):
        """Test if authentication is working"""
        url = f"{self.base_url}/v1/user-service/my/profile"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            print("Authentication successful")
            return True
        else:
            print(f"Authentication failed: {response.status_code}")
            return False
    
    def get_devices(self):
        """Get list of bound devices"""
        url = f"{self.base_url}/v1/iot-service/api/user/bind"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()

# Usage
token = os.getenv("BAMBU_TOKEN")
auth = BambuAuth(token)

if auth.test_auth():
    devices = auth.get_devices()
    print(f"Found {len(devices.get('devices', []))} devices")
```

---

## Rate Limiting

Authentication endpoints have specific rate limits:

- **Login attempts:** 5 per minute
- **Token refresh:** 10 per hour
- **Profile access:** 60 per minute
- **Device queries:** 120 per minute

Exceeding rate limits returns `429 Too Many Requests`.

---

## Support and Troubleshooting

### Debug Authentication Issues

```python
def debug_auth(token, base_url):
    import jwt
    import datetime
    
    # Decode token (without verification for debugging)
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("Token Payload:")
        print(f"  User ID: {decoded.get('user_id')}")
        print(f"  Issued: {datetime.datetime.fromtimestamp(decoded.get('iat', 0))}")
        print(f"  Expires: {datetime.datetime.fromtimestamp(decoded.get('exp', 0))}")
        
        # Check if expired
        if decoded.get('exp', 0) < time.time():
            print("  Status: EXPIRED")
        else:
            print("  Status: VALID")
            
    except Exception as e:
        print(f"Token decode error: {e}")
    
    # Test connection
    response = requests.get(
        f"{base_url}/v1/user-service/my/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"\nAPI Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
```

### Common Issues

1. **Token won't work across regions**
   - Global and China tokens are separate
   - Must use matching API endpoint

2. **Certificate signature fails**
   - Check timestamp is current (within 5 minutes)
   - Verify private key matches certificate
   - Ensure correct signature algorithm (SHA-256)

3. **Intermittent auth failures**
   - Check network connectivity
   - Verify system time is accurate
   - Implement retry logic with exponential backoff

---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management endpoints
- [API_USERS.md](API_USERS.md) - User profile endpoints
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes and responses
