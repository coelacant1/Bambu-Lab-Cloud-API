"""
Authentication and Token Management
====================================

Handles token validation, mapping, storage, and login with 2FA support.
"""

import json
import os
import requests
from typing import Dict, Optional, Callable
from pathlib import Path


class TokenManager:
    """
    Manages API token mappings and validation.
    
    Supports mapping custom tokens to real Bambu Lab tokens for proxy use.
    """
    
    def __init__(self, token_file: str = "tokens.json"):
        """
        Initialize token manager.
        
        Args:
            token_file: Path to token mapping file
        """
        self.token_file = token_file
        self.tokens = {}
        self.load()
    
    def load(self):
        """Load tokens from file"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.tokens = json.load(f)
        else:
            self.tokens = {}
    
    def save(self):
        """Save tokens to file"""
        with open(self.token_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def add_token(self, custom_token: str, real_token: str):
        """
        Add a token mapping.
        
        Args:
            custom_token: Custom token identifier
            real_token: Actual Bambu Lab access token
        """
        self.tokens[custom_token] = real_token
        self.save()
    
    def remove_token(self, custom_token: str) -> bool:
        """
        Remove a token mapping.
        
        Args:
            custom_token: Custom token to remove
            
        Returns:
            True if removed, False if not found
        """
        if custom_token in self.tokens:
            del self.tokens[custom_token]
            self.save()
            return True
        return False
    
    def validate(self, custom_token: str) -> Optional[str]:
        """
        Validate a custom token and return the real token.
        
        Args:
            custom_token: Custom token to validate
            
        Returns:
            Real Bambu Lab token if valid, None otherwise
        """
        return self.tokens.get(custom_token)
    
    def list_tokens(self) -> Dict[str, str]:
        """
        Get all token mappings.
        
        Returns:
            Dictionary with custom tokens as keys and real tokens as values
        """
        return {
            custom: f"{real[:20]}..." if len(real) > 20 else real
            for custom, real in self.tokens.items()
        }
    
    def count(self) -> int:
        """Get number of configured tokens"""
        return len(self.tokens)


class BambuAuthError(Exception):
    """Exception raised for authentication errors"""
    pass


class BambuAuthenticator:
    """
    Handles Bambu Lab login with two-factor authentication support.
    
    Supports:
    - Email/password login
    - Email verification code (2FA)
    - MFA (multi-factor authentication)
    - Token persistence to local storage
    """
    
    GLOBAL_API = "https://api.bambulab.com"
    CHINA_API = "https://api.bambulab.cn"
    
    DEFAULT_HEADERS = {
        'User-Agent': 'bambu_network_agent/01.09.05.01',
        'X-BBL-Client-Name': 'OrcaSlicer',
        'X-BBL-Client-Type': 'slicer',
        'X-BBL-Client-Version': '01.09.05.51',
        'X-BBL-Language': 'en-US',
        'X-BBL-OS-Type': 'linux',
        'X-BBL-OS-Version': '6.2.0',
        'X-BBL-Agent-Version': '01.09.05.01',
        'X-BBL-Executable-info': '{}',
        'X-BBL-Agent-OS-Type': 'linux',
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    def __init__(self, region: str = "global", token_file: Optional[str] = None):
        """
        Initialize authenticator.
        
        Args:
            region: API region - "global" or "china" (default: "global")
            token_file: Optional path to save tokens (default: ~/.bambu_token)
        """
        self.base_url = self.CHINA_API if region == "china" else self.GLOBAL_API
        self.region = region
        
        if token_file is None:
            token_file = os.path.join(str(Path.home()), ".bambu_token")
        self.token_file = token_file
        
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        
    def login(
        self,
        username: str,
        password: str,
        code_callback: Optional[Callable[[], str]] = None
    ) -> str:
        """
        Login to Bambu Lab and get access token.
        
        Handles the complete authentication flow including:
        1. Initial login attempt with username/password
        2. Email verification code if required
        3. MFA if enabled
        
        Args:
            username: Bambu Lab account email
            password: Account password
            code_callback: Optional callback function to get verification code.
                          If not provided, will prompt via input().
                          Function should return the code as a string.
        
        Returns:
            Access token string
            
        Raises:
            BambuAuthError: If authentication fails
            
        Example:
            >>> auth = BambuAuthenticator()
            >>> token = auth.login("user@email.com", "password")
            >>> # With custom code input:
            >>> def get_code():
            ...     return input("Enter code from email: ")
            >>> token = auth.login("user@email.com", "password", get_code)
        """
        auth_payload = {
            "account": username,
            "password": password,
            "apiError": ""
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/user-service/user/login",
                json=auth_payload,
                timeout=30
            )
            response.raise_for_status()
            
            if not response.text.strip():
                raise BambuAuthError("Empty response from server")
                
            data = response.json()
            
            # Check for successful login
            if data.get("success"):
                token = data.get("accessToken")
                if token:
                    self.save_token(token)
                    return token
                raise BambuAuthError("Login successful but no token received")
            
            # Handle additional authentication requirements
            login_type = data.get("loginType")
            
            if login_type == "verifyCode":
                return self._handle_email_verification(username, code_callback)
            elif login_type == "tfa":
                tfa_key = data.get("tfaKey")
                return self._handle_mfa(tfa_key, code_callback)
            else:
                error_msg = data.get("message", data.get("error", "Unknown error"))
                raise BambuAuthError(f"Login failed: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise BambuAuthError(f"Network error during login: {e}")
        except json.JSONDecodeError as e:
            raise BambuAuthError(f"Invalid response from server: {e}")
    
    def _handle_email_verification(
        self,
        email: str,
        code_callback: Optional[Callable[[], str]] = None
    ) -> str:
        """
        Handle email verification code flow.
        
        Args:
            email: User's email address
            code_callback: Optional callback to get code from user
            
        Returns:
            Access token
        """
        # Send verification code to email
        send_payload = {
            "email": email,
            "type": "codeLogin"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/user-service/user/sendemail/code",
                json=send_payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Get code from user
            if code_callback:
                code = code_callback()
            else:
                print("A verification code has been sent to your email.")
                code = input("Enter the verification code: ")
            
            # Verify the code
            verify_payload = {
                "account": email,
                "code": code
            }
            
            verify_response = self.session.post(
                f"{self.base_url}/v1/user-service/user/login",
                json=verify_payload,
                timeout=30
            )
            verify_response.raise_for_status()
            
            if not verify_response.text.strip():
                raise BambuAuthError("Empty response during verification")
                
            verify_data = verify_response.json()
            token = verify_data.get("accessToken")
            
            if token:
                self.save_token(token)
                return token
            else:
                error_msg = verify_data.get("message", "Verification failed")
                raise BambuAuthError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise BambuAuthError(f"Network error during verification: {e}")
        except json.JSONDecodeError as e:
            raise BambuAuthError(f"Invalid response during verification: {e}")
    
    def _handle_mfa(
        self,
        tfa_key: str,
        code_callback: Optional[Callable[[], str]] = None
    ) -> str:
        """
        Handle MFA (multi-factor authentication) flow.
        
        Args:
            tfa_key: TFA key from initial login response
            code_callback: Optional callback to get MFA code
            
        Returns:
            Access token
        """
        # Get MFA code from user
        if code_callback:
            code = code_callback()
        else:
            print("Multi-factor authentication required.")
            code = input("Enter your MFA code: ")
        
        verify_payload = {
            "tfaKey": tfa_key,
            "tfaCode": code
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/sign-in/tfa",
                json=verify_payload,
                timeout=30
            )
            response.raise_for_status()
            
            if not response.text.strip():
                raise BambuAuthError("Empty response during MFA")
            
            # MFA might return token in cookies
            cookies = response.cookies.get_dict()
            token = cookies.get("token")
            
            # Or in JSON response
            if not token:
                data = response.json()
                token = data.get("accessToken") or data.get("token")
            
            if token:
                self.save_token(token)
                return token
            else:
                raise BambuAuthError("MFA verification failed")
                
        except requests.exceptions.RequestException as e:
            raise BambuAuthError(f"Network error during MFA: {e}")
        except json.JSONDecodeError as e:
            raise BambuAuthError(f"Invalid response during MFA: {e}")
    
    def save_token(self, token: str) -> None:
        """
        Save token to local file.
        
        Args:
            token: Access token to save
        """
        data = {
            "region": self.region,
            "token": token
        }
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.token_file, 0o600)
            
        except Exception as e:
            # Don't fail if we can't save, just warn
            print(f"Warning: Could not save token to {self.token_file}: {e}")
    
    def load_token(self) -> Optional[str]:
        """
        Load saved token from file.
        
        Returns:
            Token string if found, None otherwise
        """
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                return data.get("token")
        except Exception as e:
            print(f"Warning: Could not load token from {self.token_file}: {e}")
        
        return None
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if a token is valid by making a test API call.
        
        Args:
            token: Token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{self.base_url}/v1/user-service/my/profile",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except:
            return False
    
    def get_or_create_token(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        code_callback: Optional[Callable[[], str]] = None,
        force_new: bool = False
    ) -> str:
        """
        Get existing token or create new one via login.
        
        First tries to load saved token. If not found or invalid,
        performs login to get new token.
        
        Args:
            username: Account email (required if no saved token)
            password: Account password (required if no saved token)
            code_callback: Optional callback for verification codes
            force_new: Force new login even if saved token exists
            
        Returns:
            Valid access token
            
        Raises:
            BambuAuthError: If login fails or credentials not provided
            
        Example:
            >>> auth = BambuAuthenticator()
            >>> # Try saved token first, login if needed
            >>> token = auth.get_or_create_token(
            ...     username="user@email.com",
            ...     password="password"
            ... )
        """
        # Try to load existing token
        if not force_new:
            token = self.load_token()
            if token and self.verify_token(token):
                return token
        
        # Need to login
        if not username or not password:
            raise BambuAuthError(
                "Username and password required for login. "
                "No valid saved token found."
            )
        
        return self.login(username, password, code_callback)
