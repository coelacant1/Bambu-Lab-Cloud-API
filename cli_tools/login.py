#!/usr/bin/env python3
"""
Bambu Lab Login CLI Tool
========================

Command-line tool to authenticate with Bambu Lab and save the token locally.
Supports email verification and MFA.

Usage:
    python login.py
    python login.py --username user@email.com --password mypass
    python login.py --region china
    python login.py --token-file /path/to/token
"""

import argparse
import sys
import getpass
from pathlib import Path

# Add parent directory to path to import bambulab
sys.path.insert(0, str(Path(__file__).parent.parent))

from bambulab import BambuAuthenticator, BambuAuthError, BambuClient


def main():
    parser = argparse.ArgumentParser(
        description="Login to Bambu Lab and save access token",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive login
  python login.py
  
  # Login with credentials
  python login.py --username user@email.com --password mypass
  
  # Use China region
  python login.py --region china
  
  # Custom token file location
  python login.py --token-file ~/.my_bambu_token
  
  # Verify existing token
  python login.py --verify-only
        """
    )
    
    parser.add_argument(
        '--username', '-u',
        help='Bambu Lab account email'
    )
    parser.add_argument(
        '--password', '-p',
        help='Account password (will prompt if not provided)'
    )
    parser.add_argument(
        '--region', '-r',
        choices=['global', 'china'],
        default='global',
        help='API region (default: global)'
    )
    parser.add_argument(
        '--token-file', '-t',
        help='Path to save token file (default: ~/.bambu_token)'
    )
    parser.add_argument(
        '--verify-only', '-v',
        action='store_true',
        help='Only verify existing token without logging in'
    )
    parser.add_argument(
        '--force-new', '-f',
        action='store_true',
        help='Force new login even if valid token exists'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test the token by fetching user profile'
    )
    
    args = parser.parse_args()
    
    # Initialize authenticator
    auth = BambuAuthenticator(region=args.region, token_file=args.token_file)
    
    print(f"Bambu Lab Authentication Tool")
    print(f"Region: {args.region}")
    print(f"Token file: {auth.token_file}")
    print()
    
    # Verify only mode
    if args.verify_only:
        token = auth.load_token()
        if not token:
            print("No saved token found")
            sys.exit(1)
        
        print("Verifying token...")
        if auth.verify_token(token):
            print("Token is valid!")
            sys.exit(0)
        else:
            print("Token is invalid or expired")
            sys.exit(1)
    
    # Get credentials
    username = args.username
    password = args.password
    
    if not username:
        username = input("Email: ")
    
    if not password:
        password = getpass.getpass("Password: ")
    
    if not username or not password:
        print("Error: Username and password are required")
        sys.exit(1)
    
    try:
        # Attempt login
        print("\nLogging in...")
        token = auth.get_or_create_token(
            username=username,
            password=password,
            force_new=args.force_new
        )
        
        print("Login successful!")
        print(f"Token saved to: {auth.token_file}")
        print(f"Token: {token[:20]}...{token[-20:]}")
        
        # Test token if requested
        if args.test:
            print("\nTesting token...")
            client = BambuClient(token=token)
            try:
                profile = client.get_user_profile()
                print("Token verified!")
                print(f"User: {profile.get('name', 'N/A')}")
                print(f"Email: {profile.get('email', 'N/A')}")
                
                # Try to get devices
                devices = client.get_devices()
                print(f"Devices: {len(devices)} found")
                for device in devices:
                    print(f"  - {device.get('name', 'Unknown')} ({device.get('dev_id', 'N/A')})")
                
            except Exception as e:
                print(f"Token test failed: {e}")
                sys.exit(1)
        
        sys.exit(0)
        
    except BambuAuthError as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nLogin cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
