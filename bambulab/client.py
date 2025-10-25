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
    
    def get_ams_filaments(self, device_id: str) -> Dict:
        """
        Get AMS (Automatic Material System) filament information.
        
        Returns detailed information about AMS units, trays, and loaded filaments.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Dictionary with AMS units, trays, and filament data
            
        Example:
            >>> ams_info = client.get_ams_filaments("01P00A123456789")
            >>> for unit in ams_info.get('ams_units', []):
            ...     print(f"AMS Unit {unit['unit_id']}:")
            ...     for tray in unit.get('trays', []):
            ...         print(f"  Tray {tray['tray_id']}: {tray.get('filament_type')}")
        """
        # Get from device version which includes AMS data
        version = self.get_device_version(device_id)
        
        result = {
            'device_id': device_id,
            'ams_units': [],
            'total_trays': 0,
            'has_ams': False
        }
        
        # Extract AMS info from version data
        if 'devices' in version:
            for dev in version['devices']:
                if dev.get('dev_id') == device_id:
                    if 'ams' in dev:
                        result['has_ams'] = True
                        ams_list = dev['ams'] if isinstance(dev['ams'], list) else [dev['ams']]
                        
                        for idx, ams in enumerate(ams_list):
                            unit_info = {
                                'unit_id': idx,
                                'sw_version': ams.get('sw_ver'),
                                'hw_version': ams.get('hw_ver'),
                                'trays': [],
                                'raw_data': ams  # Include all raw data
                            }
                            
                            # Extract tray/filament info if available
                            if 'tray' in ams:
                                trays = ams['tray'] if isinstance(ams['tray'], list) else [ams['tray']]
                                for tray in trays:
                                    tray_info = {
                                        'tray_id': tray.get('id', tray.get('tray_id')),
                                        'filament_type': tray.get('tray_type', tray.get('type')),
                                        'filament_color': tray.get('tray_color', tray.get('color')),
                                        'filament_weight': tray.get('tray_weight', tray.get('weight')),
                                        'temperature': tray.get('nozzle_temp_min', tray.get('temp')),
                                        'remaining': tray.get('remain', tray.get('remaining')),
                                        'raw_data': tray  # Include all raw tray data
                                    }
                                    unit_info['trays'].append(tray_info)
                                    result['total_trays'] += 1
                            
                            result['ams_units'].append(unit_info)
                    break
        
        return result
    
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
    
    def start_print_job(
        self,
        device_id: str,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        file_url: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> Dict:
        """
        Start a print job on a device.
        
        Args:
            device_id: Device serial number
            file_id: File ID (if file already uploaded to cloud)
            file_name: Name of the file
            file_url: Direct URL to the file
            settings: Print settings (layer_height, infill, speed, etc.)
            
        Returns:
            Print job information with job_id and status
            
        Example:
            >>> job = client.start_print_job(
            ...     device_id="01P00A123456789",
            ...     file_id="abc123",
            ...     file_name="model.3mf",
            ...     settings={"layer_height": 0.2, "infill": 20}
            ... )
        """
        data = {'device_id': device_id}
        
        if file_id:
            data['file_id'] = file_id
        if file_name:
            data['file_name'] = file_name
        if file_url:
            data['file_url'] = file_url
        if settings:
            data['settings'] = settings
            
        return self.post('v1/iot-service/api/user/print', data=data)
    
    def start_cloud_print(
        self,
        device_id: str,
        filename: str,
        settings: Optional[Dict] = None
    ) -> Dict:
        """
        Start a print job from a cloud-uploaded file.
        
        Searches for the file by name in your cloud storage and starts printing.
        
        Args:
            device_id: Device serial number
            filename: Name of the file (e.g., "api_test.3mf")
            settings: Optional print settings
            
        Returns:
            Print job information
            
        Example:
            >>> # After uploading api_test.3mf
            >>> result = client.start_cloud_print(
            ...     device_id="01P00A123456789",
            ...     filename="api_test.3mf"
            ... )
            >>> print(f"Print started: {result}")
        """
        # Try to find the file
        files = self.get_cloud_files()
        
        # Look for file by name
        target_file = None
        for f in files:
            if f.get('name') == filename or f.get('file_name') == filename or f.get('title') == filename:
                target_file = f
                break
        
        if not target_file:
            raise BambuAPIError(f"File '{filename}' not found in cloud storage. Upload it first.")
        
        # Start print with file info
        file_id = target_file.get('file_id') or target_file.get('model_id') or target_file.get('id')
        file_url = target_file.get('file_url') or target_file.get('url')
        
        return self.start_print_job(
            device_id=device_id,
            file_id=file_id,
            file_name=filename,
            file_url=file_url,
            settings=settings
        )
    
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
        """
        Get list of projects/files from cloud.
        
        Returns:
            List of project dictionaries with file info
        """
        response = self.get('v1/iot-service/api/user/project')
        return response.get('projects', [])
    
    def get_cloud_files(self) -> List[Dict]:
        """
        Get list of uploaded files from cloud storage.
        
        Tries multiple endpoints to find your uploaded files.
        
        Returns:
            List of file dictionaries with file_id, name, url, etc.
            
        Example:
            >>> files = client.get_cloud_files()
            >>> for f in files:
            ...     print(f"File: {f['name']}, ID: {f['file_id']}")
        """
        # Try projects endpoint
        try:
            projects = self.get_projects()
            files = []
            for project in projects:
                if 'files' in project:
                    files.extend(project['files'])
                elif 'model_id' in project:
                    # Project itself is a file
                    files.append(project)
            if files:
                return files
        except:
            pass
        
        # Try direct files endpoint
        try:
            response = self.get('v1/iot-service/api/user/files')
            return response.get('files', [])
        except:
            pass
        
        # Try tasks endpoint (may show uploaded files)
        try:
            return self.get_tasks()
        except:
            pass
        
        return []
    
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
    
    def get_task(self, task_id: str) -> Dict:
        """
        Get details of a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task details dictionary
        """
        return self.get(f'v1/iot-service/api/user/task/{task_id}')
    
    def create_task(self, model_id: str, title: str, device_id: str, **kwargs) -> Dict:
        """
        Create a new print task.
        
        Args:
            model_id: Model/file ID to print
            title: Task title/name
            device_id: Device serial number to print on
            **kwargs: Additional task parameters (profile_id, plate_index, etc.)
            
        Returns:
            Created task information
            
        Example:
            >>> task = client.create_task(
            ...     model_id="model_abc123",
            ...     title="My Print Job",
            ...     device_id="01P00A123456789",
            ...     profile_id=1,
            ...     plate_index=1
            ... )
        """
        data = {
            'modelId': model_id,
            'title': title,
            'deviceId': device_id,
            **kwargs
        }
        return self.post('v1/user-service/my/task', data=data)
    
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
    
    def get_cloud_video_url(self, device_id: str) -> Dict:
        """
        Get cloud video stream URL for remote access.
        
        Some Bambu printers support video streaming through the cloud
        when not on local network. This gets the cloud stream URL.
        
        Args:
            device_id: Device serial number
            
        Returns:
            Dictionary with video stream information
            
        Example:
            >>> stream_info = client.get_cloud_video_url("01S00A000000000")
            >>> if 'url' in stream_info:
            ...     print(f"Cloud stream URL: {stream_info['url']}")
        """
        # Try multiple potential endpoints
        endpoints = [
            f'v1/iot-service/api/user/device/{device_id}/video',
            f'v1/iot-service/api/user/device/{device_id}/stream',
            'v1/iot-service/api/user/video/stream',
        ]
        
        for endpoint in endpoints:
            try:
                params = {'dev_id': device_id}
                result = self.get(endpoint, params=params)
                if result and ('url' in result or 'stream_url' in result):
                    return result
            except BambuAPIError as e:
                if '404' not in str(e) and '405' not in str(e):
                    raise
                continue
        
        # If no endpoint worked, return the TTCode which can be used
        # with the local stream endpoints
        return self.get_camera_credentials(device_id)
    
    def get_camera_urls(self, device_id: str) -> Dict:
        """
        Get all camera-related URLs including AWS snapshots.
        
        Returns URLs for:
        - Snapshot images (JPEG from AWS S3)
        - Video stream info (TUTK credentials)
        - Any camera URLs in device data
        
        Args:
            device_id: Device serial number
            
        Returns:
            Dictionary with camera URLs and credentials
            
        Example:
            >>> urls = client.get_camera_urls(device_id)
            >>> if 'snapshot_url' in urls:
            ...     print(f"Snapshot: {urls['snapshot_url']}")
            >>> print(f"TTCode: {urls['ttcode']}")
        """
        # Get TTCode/credentials first
        creds = self.get_camera_credentials(device_id)
        result = creds.copy()
        
        # Try to get snapshot URLs from device info
        try:
            devices = self.get_devices()
            device = next((d for d in devices if d.get('dev_id') == device_id), None)
            
            if device:
                # Check for camera/ipcam URLs in device data
                if 'ipcam' in device:
                    result['ipcam_info'] = device['ipcam']
                
                # Look for any camera/snapshot URLs
                for key in device.keys():
                    if 'camera' in key.lower() or 'snapshot' in key.lower() or 'image' in key.lower() or 'video' in key.lower():
                        value = device[key]
                        if isinstance(value, str) and ('http' in value or 's3' in value or 'amazonaws' in value):
                            result[key] = value
        except:
            pass
        
        # Try dedicated snapshot endpoint
        try:
            snapshot_info = self.get(f'v1/iot-service/api/user/device/{device_id}/snapshot')
            if snapshot_info:
                result.update(snapshot_info)
        except:
            pass
        
        return result
    
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
    
    def mark_notification_read(self, notification_id: str, read: bool = True) -> Dict:
        """
        Mark a notification as read or unread.
        
        Args:
            notification_id: Notification ID
            read: True to mark as read, False to mark as unread (default: True)
            
        Returns:
            Update result dictionary
            
        Example:
            >>> client.mark_notification_read("notif_123")
            >>> client.mark_notification_read("notif_456", read=False)
        """
        data = {
            'notification_id': notification_id,
            'read': read
        }
        return self.put('v1/iot-service/api/user/notification', data=data)
    
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
    
    def get_upload_url(self, filename: Optional[str] = None, size: Optional[int] = None) -> Dict:
        """
        Get upload URL information for uploading files to cloud.
        
        Args:
            filename: Optional filename to upload
            size: Optional file size in bytes
            
        Returns:
            Dictionary with upload_url, upload_ticket, etc.
        """
        params = {}
        if filename:
            params['filename'] = filename
        if size:
            params['size'] = size
        
        return self.get('v1/iot-service/api/user/upload', params=params)
    
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
        file_size = os.path.getsize(file_path)
        upload_info = self.get_upload_url(filename=filename, size=file_size)
        upload_url = upload_info.get('upload_url')
        upload_ticket = upload_info.get('upload_ticket')
        urls_array = upload_info.get('urls', [])
        
        # Handle different response formats
        if not upload_url and urls_array:
            # Format: [{"type": "filename", "url": "https://..."}, {"type": "size", "url": "..."}]
            if isinstance(urls_array, list) and len(urls_array) > 0:
                # Find the filename URL entry
                for entry in urls_array:
                    if isinstance(entry, dict) and entry.get('type') == 'filename':
                        upload_url = entry.get('url')
                        break
                
                # If no filename type found, use first URL
                if not upload_url:
                    first_entry = urls_array[0]
                    if isinstance(first_entry, dict):
                        upload_url = first_entry.get('url')
                    else:
                        upload_url = first_entry
            else:
                # Direct URL string in array
                upload_url = urls_array[0] if urls_array else None
        
        if not upload_url:
            raise BambuAPIError("Failed to get upload URL from server. Response: " + str(upload_info))
        
        # Step 2: Upload file to S3-compatible storage
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
            # For S3 signed URLs, we must match EXACTLY what was signed
            # Some signed URLs fail if you add headers that weren't included in the signature
            # Try with minimal headers first
            response = requests.put(
                upload_url,
                data=file_content,
                headers={},  # Empty headers - let requests handle it
                timeout=300  # 5 minute timeout for large files
            )
            
            if response.status_code >= 400:
                raise BambuAPIError(
                    f"File upload failed ({response.status_code}): {response.text}"
                )
            
            # S3 returns XML or empty on success
            # Build result from what we know
            result = {
                'filename': filename,
                'file_size': file_size,
                'upload_url': upload_url,
                'status_code': response.status_code
            }
        
        # Step 3: Upload size file if provided
        if urls_array:
            for entry in urls_array:
                if isinstance(entry, dict) and entry.get('type') == 'size':
                    size_url = entry.get('url')
                    if size_url:
                        # Upload size information
                        try:
                            size_response = requests.put(
                                size_url,
                                data=str(file_size).encode(),
                                headers={'Content-Type': 'text/plain'},
                                timeout=30
                            )
                        except:
                            pass  # Size upload is optional
        
        return result
        
        return {
            'file_id': result.get('file_id'),
            'file_url': result.get('file_url') or result.get('url'),
            'file_size': os.path.getsize(file_path),
            'filename': filename
        }
