"""
Bambu Lab Local API Client
===========================

Provides direct local network communication with Bambu Lab printers.
Supports FTP file upload and local printing commands via MQTT.

Note: Requires printer to have local mode enabled (some newer firmware versions
may have this disabled by default).
"""

import os
import hashlib
from ftplib import FTP, FTP_TLS
from typing import Optional, Dict, Any
from pathlib import Path
import json


class LocalAPIError(Exception):
    """Error communicating with printer locally"""
    pass


class LocalFTPClient:
    """
    FTP client for uploading files directly to printer.
    
    Supports uploading 3MF, gcode, and other files to the printer's SD card
    or internal storage for local printing.
    """
    
    def __init__(self, printer_ip: str, access_code: str, use_tls: bool = False):
        """
        Initialize local FTP client.
        
        Args:
            printer_ip: IP address of printer
            access_code: Printer access code (dev_access_code)
            use_tls: Use FTPS (TLS encryption) if supported
        """
        self.printer_ip = printer_ip
        self.access_code = access_code
        self.use_tls = use_tls
        self.ftp: Optional[FTP] = None
    
    def connect(self):
        """
        Connect to printer FTP server.
        
        Raises:
            LocalAPIError: If connection fails
        """
        try:
            if self.use_tls:
                self.ftp = FTP_TLS()
            else:
                self.ftp = FTP()
            
            self.ftp.connect(self.printer_ip, timeout=30)
            self.ftp.login(user='bblp', passwd=self.access_code)
            
            if self.use_tls and isinstance(self.ftp, FTP_TLS):
                self.ftp.prot_p()  # Enable secure data connection
                
        except Exception as e:
            raise LocalAPIError(f"Failed to connect to printer FTP: {e}")
    
    def disconnect(self):
        """Close FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.ftp = None
    
    def upload_file(
        self,
        local_path: str,
        remote_path: Optional[str] = None,
        target_dir: str = "/"
    ) -> Dict[str, Any]:
        """
        Upload a file to the printer.
        
        Args:
            local_path: Path to local file to upload
            remote_path: Remote filename (default: use local filename)
            target_dir: Target directory on printer (default: root)
            
        Returns:
            Dictionary with upload info including MD5 hash
            
        Example:
            >>> client = LocalFTPClient("192.168.1.100", "12345678")
            >>> client.connect()
            >>> result = client.upload_file("model.3mf")
            >>> print(result['md5'])
            
        Raises:
            LocalAPIError: If upload fails
        """
        if not self.ftp:
            raise LocalAPIError("Not connected. Call connect() first.")
        
        local_path_obj = Path(local_path)
        if not local_path_obj.exists():
            raise LocalAPIError(f"File not found: {local_path}")
        
        if remote_path is None:
            remote_path = local_path_obj.name
        
        # Calculate MD5 for verification
        md5_hash = self._calculate_md5(local_path)
        file_size = local_path_obj.stat().st_size
        
        try:
            # Change to target directory
            if target_dir != "/":
                try:
                    self.ftp.cwd(target_dir)
                except:
                    # Try to create directory if it doesn't exist
                    self.ftp.mkd(target_dir)
                    self.ftp.cwd(target_dir)
            
            # Upload file
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f)
            
            return {
                'filename': remote_path,
                'local_path': str(local_path_obj.absolute()),
                'remote_path': f"{target_dir}/{remote_path}".replace('//', '/'),
                'size': file_size,
                'md5': md5_hash
            }
            
        except Exception as e:
            raise LocalAPIError(f"Failed to upload file: {e}")
    
    def list_files(self, directory: str = "/") -> list:
        """
        List files in a directory on the printer.
        
        Args:
            directory: Directory path to list
            
        Returns:
            List of filenames
        """
        if not self.ftp:
            raise LocalAPIError("Not connected. Call connect() first.")
        
        try:
            self.ftp.cwd(directory)
            return self.ftp.nlst()
        except Exception as e:
            raise LocalAPIError(f"Failed to list files: {e}")
    
    def delete_file(self, remote_path: str):
        """
        Delete a file from the printer.
        
        Args:
            remote_path: Path to file on printer
        """
        if not self.ftp:
            raise LocalAPIError("Not connected. Call connect() first.")
        
        try:
            self.ftp.delete(remote_path)
        except Exception as e:
            raise LocalAPIError(f"Failed to delete file: {e}")
    
    @staticmethod
    def _calculate_md5(file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    def __enter__(self):
        """Context manager support."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.disconnect()


class LocalPrintClient:
    """
    Helper for sending local print commands via MQTT.
    
    This integrates with the MQTT client to send print commands
    for files uploaded via FTP.
    """
    
    @staticmethod
    def create_print_command(
        file_path: str,
        plate_index: int = 1,
        use_ams: bool = False,
        ams_mapping: str = "",
        timelapse: bool = True,
        bed_leveling: bool = True,
        flow_calibration: bool = True,
        vibration_calibration: bool = True,
        layer_inspect: bool = True
    ) -> Dict[str, Any]:
        """
        Create a print command for local file printing.
        
        Args:
            file_path: Path to file on printer (e.g., "/mymodel.3mf")
            plate_index: Plate index in 3MF file (usually 1)
            use_ams: Use Automatic Material System
            ams_mapping: AMS slot mapping
            timelapse: Enable timelapse recording
            bed_leveling: Enable bed leveling
            flow_calibration: Enable flow calibration
            vibration_calibration: Enable vibration calibration
            layer_inspect: Enable layer inspection
            
        Returns:
            Dictionary containing print command to send via MQTT
            
        Example:
            >>> from bambulab import MQTTClient, LocalPrintClient
            >>> mqtt = MQTTClient("uid", "token", "device_serial")
            >>> mqtt.connect()
            >>> 
            >>> # After uploading file via FTP
            >>> cmd = LocalPrintClient.create_print_command("/model.3mf")
            >>> mqtt.publish_command(cmd)
        """
        # Construct the parameter for the plate gcode
        param = f"Metadata/plate_{plate_index}.gcode"
        
        # Determine URL protocol based on file path
        # Files on SD card use ftp://, internal storage can use file://
        if file_path.startswith('/'):
            # Assume SD card for absolute paths
            url = f"ftp://{file_path}"
        else:
            url = f"file:///{file_path}"
        
        return {
            "print": {
                "sequence_id": "0",
                "command": "project_file",
                "param": param,
                "project_id": "0",
                "profile_id": "0",
                "task_id": "0",
                "subtask_id": "0",
                "subtask_name": "",
                "url": url,
                "md5": "",  # Optional: add MD5 hash if available
                "timelapse": timelapse,
                "bed_type": "auto",
                "bed_levelling": bed_leveling,
                "flow_cali": flow_calibration,
                "vibration_cali": vibration_calibration,
                "layer_inspect": layer_inspect,
                "ams_mapping": ams_mapping,
                "use_ams": use_ams
            }
        }
    
    @staticmethod
    def create_gcode_print_command(
        gcode_path: str,
        use_ams: bool = False,
        ams_mapping: str = "",
        timelapse: bool = True
    ) -> Dict[str, Any]:
        """
        Create a print command for raw gcode file.
        
        Args:
            gcode_path: Path to gcode file on printer
            use_ams: Use Automatic Material System
            ams_mapping: AMS slot mapping
            timelapse: Enable timelapse recording
            
        Returns:
            Dictionary containing gcode print command
        """
        # For gcode files, we use gcode_file command
        if gcode_path.startswith('/'):
            url = f"ftp://{gcode_path}"
        else:
            url = f"file:///{gcode_path}"
        
        return {
            "print": {
                "sequence_id": "0",
                "command": "gcode_file",
                "param": "",
                "url": url,
                "timelapse": timelapse,
                "use_ams": use_ams,
                "ams_mapping": ams_mapping
            }
        }


def upload_and_print(
    printer_ip: str,
    access_code: str,
    file_path: str,
    mqtt_client = None,
    **print_kwargs
) -> Dict[str, Any]:
    """
    Convenience function to upload file and start printing.
    
    Args:
        printer_ip: IP address of printer
        access_code: Printer access code
        file_path: Path to local file to upload and print
        mqtt_client: Optional MQTT client instance for sending print command
        **print_kwargs: Additional arguments for create_print_command
        
    Returns:
        Dictionary with upload result and print command
        
    Example:
        >>> from bambulab import MQTTClient
        >>> mqtt = MQTTClient("uid", "token", "device_serial")
        >>> mqtt.connect()
        >>> 
        >>> result = upload_and_print(
        ...     "192.168.1.100",
        ...     "12345678",
        ...     "my_model.3mf",
        ...     mqtt_client=mqtt
        ... )
    """
    # Upload file
    with LocalFTPClient(printer_ip, access_code) as ftp:
        upload_result = ftp.upload_file(file_path)
    
    # Create print command
    remote_path = f"/{upload_result['filename']}"
    print_command = LocalPrintClient.create_print_command(remote_path, **print_kwargs)
    
    # Send print command if MQTT client provided
    if mqtt_client:
        mqtt_client.publish_command(print_command)
    
    return {
        'upload': upload_result,
        'print_command': print_command,
        'started': mqtt_client is not None
    }
