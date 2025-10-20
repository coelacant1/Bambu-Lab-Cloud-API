"""
Authentication and Token Management
====================================

Handles token validation, mapping, and storage.
"""

import json
import os
from typing import Dict, Optional


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
        Get all token mappings (masked).
        
        Returns:
            Dictionary with custom tokens as keys and masked real tokens as values
        """
        return {
            custom: f"{real[:20]}..." if len(real) > 20 else real
            for custom, real in self.tokens.items()
        }
    
    def count(self) -> int:
        """Get number of configured tokens"""
        return len(self.tokens)
