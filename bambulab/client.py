"""
Bambu Lab HTTP API Client
==========================

Provides a unified interface for interacting with the Bambu Lab Cloud API.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class BambuAPIError(Exception):
    """Base exception for Bambu API errors"""
    pass


class BambuClient:
    """
    HTTP client for Bambu Lab Cloud API.
    
    Handles authentication, request formatting, and response parsing.
    """
    
    BASE_URL = "https://api.bambulab.com"
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, token: str, timeout: int = None):
        """
        Initialize the Bambu API client.
        
        Args:
            token: Bambu Lab access token
            timeout: Request timeout in seconds (default: 30)
        """
        self.token = token
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to BASE_URL)
            params: Query parameters
            data: Request body data
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            BambuAPIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=kwargs.get('timeout', self.timeout)
            )
            
            # Check for errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', response.text)
                except:
                    error_msg = response.text
                raise BambuAPIError(
                    f"API request failed ({response.status_code}): {error_msg}"
                )
            
            # Parse response
            if response.content:
                return response.json()
            return None
            
        except requests.exceptions.RequestException as e:
            raise BambuAPIError(f"Request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Any:
        """Make a GET request"""
        return self._request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """Make a POST request"""
        return self._request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """Make a PUT request"""
        return self._request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Any:
        """Make a DELETE request"""
        return self._request('DELETE', endpoint, **kwargs)
    
    # ===== Device Management =====
    
    def get_devices(self) -> List[Dict]:
        """
        Get list of bound devices.
        
        Returns:
            List of device dictionaries
        """
        response = self.get('v1/iot-service/api/user/bind')
        return response.get('devices', [])
    
    def get_device_version(self, device_id: str) -> Dict:
        """
        Get firmware version info for a device.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Version information dictionary
        """
        return self.get('v1/iot-service/api/user/device/version', 
                       params={'dev_id': device_id})
    
    def get_device_versions(self) -> Dict:
        """
        Get firmware versions for all devices.
        
        Alias for get_device_version without device_id parameter.
        Returns version information for all user devices.
        
        Returns:
            Version information dictionary
        """
        return self.get('v1/iot-service/api/user/device/version')
    
    def get_print_status(self, force: bool = False) -> Dict:
        """
        Get print status for all devices.
        
        Args:
            force: Force refresh (bypass cache)
            
        Returns:
            Print status dictionary
        """
        params = {'force': 'true' if force else 'false'}
        return self.get('v1/iot-service/api/user/print', params=params)
    
    # ===== User Management =====
    
    def get_user_profile(self) -> Dict:
        """Get user profile information"""
        return self.get('v1/user-service/my/profile')
    
    def get_user_info(self) -> Dict:
        """
        Get user preference/info from design service.
        
        This includes the user UID needed for MQTT connections.
        
        Returns:
            User info including UID
        """
        return self.get('v1/design-user-service/my/preference')
    
    def update_user_profile(self, data: Dict) -> Dict:
        """Update user profile"""
        return self.put('v1/user-service/my/profile', data=data)
    
    # ===== Project Management =====
    
    def get_projects(self) -> List[Dict]:
        """Get list of projects"""
        response = self.get('v1/iot-service/api/user/project')
        return response.get('projects', [])
    
    def create_project(self, name: str, **kwargs) -> Dict:
        """Create a new project"""
        data = {'name': name, **kwargs}
        return self.post('v1/iot-service/api/user/project', data=data)
    
    def get_tasks(self) -> List[Dict]:
        """
        Get list of print tasks.
        
        Returns:
            List of task dictionaries
        """
        response = self.get('v1/iot-service/api/user/task')
        return response.get('tasks', response.get('hits', []))
    
    def get_project(self, project_id: str) -> Dict:
        """
        Get details of a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project details dictionary
        """
        return self.get(f'v1/iot-service/api/user/project/{project_id}')
    
    # ===== Camera/Webcam Access =====
    
    def get_camera_credentials(self, device_id: str) -> Dict:
        """
        Get temporary credentials for accessing printer webcam/camera.
        
        Returns ttcode, passwd, and authkey needed to connect to the
        printer's video stream.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Dictionary with 'ttcode', 'passwd', 'authkey' for webcam access
            
        Example:
            >>> credentials = client.get_camera_credentials("01S00A000000000")
            >>> ttcode = credentials['ttcode']
            >>> passwd = credentials['passwd']
            >>> authkey = credentials['authkey']
            >>> # Use these to connect to video stream
        """
        data = {'dev_id': device_id}
        return self.post('v1/iot-service/api/user/ttcode', data=data)
    
    def get_ttcode(self, device_id: str) -> Dict:
        """
        Alias for get_camera_credentials().
        
        Get TTCode for webcam access.
        """
        return self.get_camera_credentials(device_id)
    
    # ===== Notifications =====
    
    def get_notifications(self, action: Optional[str] = None, unread_only: bool = False) -> Dict:
        """
        Get user notifications.
        
        Args:
            action: Filter by action type (e.g., 'upload', 'import_mesh')
            unread_only: Only return unread notifications
            
        Returns:
            Notifications dictionary
            
        Example:
            >>> notifications = client.get_notifications(action='upload')
            >>> unread = client.get_notifications(unread_only=True)
        """
        params = {}
        if action:
            params['action'] = action
        if unread_only:
            params['unread'] = 'true'
        return self.get('v1/iot-service/api/user/notification', params=params)
    
    def get_messages(self, message_type: Optional[str] = None, after: Optional[str] = None, limit: int = 20) -> Dict:
        """
        Get user messages.
        
        Args:
            message_type: Filter by message type
            after: Get messages after this ID (for pagination)
            limit: Maximum number of messages to return (default 20)
            
        Returns:
            Messages dictionary
        """
        params = {'limit': limit}
        if message_type:
            params['type'] = message_type
        if after:
            params['after'] = after
        return self.get('v1/user-service/my/messages', params=params)
    
    # ===== Slicer Settings =====
    
    def get_slicer_settings(self, version: Optional[str] = None, setting_id: Optional[str] = None) -> Dict:
        """
        Get slicer settings/profiles.
        
        Args:
            version: Slicer version (e.g., '01.03.00.13')
            setting_id: Specific setting ID to retrieve
            
        Returns:
            Slicer settings dictionary
            
        Example:
            >>> settings = client.get_slicer_settings(version='01.03.00.13')
            >>> specific = client.get_slicer_settings(setting_id='abc123')
        """
        if setting_id:
            return self.get(f'v1/iot-service/api/slicer/setting/{setting_id}')
        
        params = {}
        if version:
            params['version'] = version
        return self.get('v1/iot-service/api/slicer/setting', params=params)
    
    def get_slicer_resources(self, resource_type: Optional[str] = None, version: Optional[str] = None) -> Dict:
        """
        Get slicer resources (plugins, presets, etc.).
        
        Args:
            resource_type: Type of resource (e.g., 'slicer/plugins/cloud')
            version: Version filter
            
        Returns:
            Slicer resources dictionary
        """
        params = {}
        if resource_type:
            params['type'] = resource_type
        if version:
            params['version'] = version
        return self.get('v1/iot-service/api/slicer/resource', params=params)
    
    # ===== Device Management =====
    
    def bind_device(self, device_id: str, device_name: str, bind_code: str) -> Dict:
        """
        Bind a new device to your account.
        
        Args:
            device_id: Device serial number
            device_name: Friendly name for the device
            bind_code: 8-digit bind code from printer
            
        Returns:
            Bind result dictionary
            
        Example:
            >>> result = client.bind_device(
            ...     device_id="01P00A123456789",
            ...     device_name="My P1S",
            ...     bind_code="12345678"
            ... )
        """
        data = {
            'device_id': device_id,
            'device_name': device_name,
            'bind_code': bind_code
        }
        return self.post('v1/iot-service/api/user/bind', data=data)
    
    def unbind_device(self, device_id: str) -> Dict:
        """
        Unbind a device from your account.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Unbind result dictionary
        """
        return self.delete('v1/iot-service/api/user/bind', params={'dev_id': device_id})
    
    def get_device_info(self, device_id: str) -> Dict:
        """
        Get detailed information about a specific device.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Device information dictionary
        """
        return self.get('v1/iot-service/api/user/device/info', params={'device_id': device_id})
    
    # ===== Utility Methods =====
    
    def get_upload_url(self) -> Dict:
        """Get upload URL information"""
        return self.get('v1/iot-service/api/user/upload')
    
    def upload_file(
        self,
        file_path: str,
        filename: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Upload a file (3MF) to Bambu Cloud.
        
        Args:
            file_path: Path to the file to upload
            filename: Override filename (default: use file_path basename)
            project_id: Optional project ID to associate file with
            
        Returns:
            Dictionary with file_id, file_url, and file_size
            
        Example:
            >>> result = client.upload_file("model.3mf")
            >>> print(result['file_url'])
            
        Raises:
            BambuAPIError: If upload fails
        """
        import os
        from pathlib import Path
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise BambuAPIError(f"File not found: {file_path}")
        
        if filename is None:
            filename = file_path_obj.name
        
        # Step 1: Get upload URL
        upload_info = self.get_upload_url()
        upload_url = upload_info.get('upload_url')
        upload_ticket = upload_info.get('upload_ticket')
        
        if not upload_url:
            raise BambuAPIError("Failed to get upload URL from server")
        
        # Step 2: Upload file to provided URL
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            data = {}
            if project_id:
                data['project_id'] = project_id
            if upload_ticket:
                data['ticket'] = upload_ticket
            
            # Upload without standard auth headers (direct to storage)
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for large files
            )
            
            if response.status_code >= 400:
                raise BambuAPIError(
                    f"File upload failed ({response.status_code}): {response.text}"
                )
            
            result = response.json() if response.content else {}
        
        # Step 3: Confirm upload (if needed)
        if upload_ticket:
            confirm_data = {
                'ticket': upload_ticket,
                'filename': filename
            }
            self.post('v1/iot-service/api/user/upload/confirm', data=confirm_data)
        
        return {
            'file_id': result.get('file_id'),
            'file_url': result.get('file_url') or result.get('url'),
            'file_size': os.path.getsize(file_path),
            'filename': filename
        }
