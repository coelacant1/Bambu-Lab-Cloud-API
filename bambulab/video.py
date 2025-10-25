"""
Bambu Lab Video/Webcam Stream Handler
======================================

Provides access to printer camera streams for different printer models.

- X1 series: RTSP video stream
- A1/P1 series: JPEG frame stream over TCP
"""

import socket
import struct
import ssl
from typing import Optional, Generator
from pathlib import Path


class VideoStreamError(Exception):
    """Error accessing video stream"""
    pass


class RTSPStream:
    """
    RTSP video stream handler for X1 series printers.
    
    X1 printers provide RTSP video streams over TLS on port 322.
    """
    
    def __init__(self, printer_ip: str, access_code: str):
        """
        Initialize RTSP stream connection.
        
        Args:
            printer_ip: IP address of printer
            access_code: Printer access code (dev_access_code)
        """
        self.printer_ip = printer_ip
        self.access_code = access_code
        self.url = f"rtsps://{printer_ip}:322/streaming/live/1"
    
    def get_stream_url(self) -> str:
        """
        Get RTSP stream URL.
        
        Use with media players like VLC, ffmpeg, or cv2.VideoCapture.
        
        Returns:
            RTSP URL with authentication
            
        Example:
            >>> stream = RTSPStream("192.168.1.100", "12345678")
            >>> url = stream.get_stream_url()
            >>> # Use with VLC, ffmpeg, OpenCV, etc.
            >>> import cv2
            >>> cap = cv2.VideoCapture(url)
        """
        return f"rtsps://bblp:{self.access_code}@{self.printer_ip}:322/streaming/live/1"
    
    def get_credentials(self) -> tuple[str, str]:
        """
        Get username and password for RTSP authentication.
        
        Returns:
            Tuple of (username, password)
        """
        return ("bblp", self.access_code)


class JPEGFrameStream:
    """
    JPEG frame stream handler for A1 and P1 series printers.
    
    These printers stream 1280x720 JPEG images over a TCP connection on port 6000.
    """
    
    FRAME_START = b'\xff\xd8'  # JPEG Start of Image
    FRAME_END = b'\xff\xd9'    # JPEG End of Image
    
    def __init__(self, printer_ip: str, access_code: str):
        """
        Initialize JPEG frame stream.
        
        Args:
            printer_ip: IP address of printer
            access_code: Printer access code (dev_access_code)
        """
        self.printer_ip = printer_ip
        self.access_code = access_code
        self.socket: Optional[ssl.SSLSocket] = None
    
    def connect(self):
        """
        Connect to printer video stream.
        
        Raises:
            VideoStreamError: If connection or authentication fails
        """
        try:
            # Create socket
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.settimeout(10)
            
            # Wrap with TLS
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            self.socket = context.wrap_socket(raw_socket)
            self.socket.connect((self.printer_ip, 6000))
            
            # Send authentication packet
            self._authenticate()
            
        except Exception as e:
            if self.socket:
                self.socket.close()
                self.socket = None
            raise VideoStreamError(f"Failed to connect: {e}")
    
    def _authenticate(self):
        """Send authentication packet to printer."""
        username = b'bblp'
        password = self.access_code.encode('ascii')
        
        # Build authentication packet
        # Format: size(4) | type(4) | flags(4) | reserved(4) | username(32) | password(32)
        auth_packet = struct.pack('<I', 0x40)  # Payload size
        auth_packet += struct.pack('<I', 0x3000)  # Type
        auth_packet += struct.pack('<I', 0)  # Flags
        auth_packet += struct.pack('<I', 0)  # Reserved
        auth_packet += username.ljust(32, b'\x00')  # Username padded to 32 bytes
        auth_packet += password.ljust(32, b'\x00')  # Password padded to 32 bytes
        
        self.socket.send(auth_packet)
    
    def _recv_exact(self, size: int) -> bytes:
        """Receive exactly size bytes from socket."""
        data = b''
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                raise VideoStreamError("Connection closed")
            data += chunk
        return data
    
    def get_frame(self) -> bytes:
        """
        Get a single JPEG frame from the stream.
        
        Returns:
            JPEG image data as bytes
            
        Raises:
            VideoStreamError: If frame cannot be received
            
        Example:
            >>> stream = JPEGFrameStream("192.168.1.100", "12345678")
            >>> stream.connect()
            >>> frame = stream.get_frame()
            >>> with open('frame.jpg', 'wb') as f:
            ...     f.write(frame)
        """
        if not self.socket:
            raise VideoStreamError("Not connected. Call connect() first.")
        
        try:
            # Read header (16 bytes)
            header = self._recv_exact(16)
            payload_size, itrack, flags, reserved = struct.unpack('<IIII', header)
            
            # Read image data
            image_data = self._recv_exact(payload_size)
            
            # Verify JPEG markers
            if not image_data.startswith(self.FRAME_START):
                raise VideoStreamError("Invalid JPEG start marker")
            if not image_data.endswith(self.FRAME_END):
                raise VideoStreamError("Invalid JPEG end marker")
            
            return image_data
            
        except Exception as e:
            raise VideoStreamError(f"Failed to receive frame: {e}")
    
    def stream_frames(self) -> Generator[bytes, None, None]:
        """
        Generate continuous stream of JPEG frames.
        
        Yields:
            JPEG image data as bytes
            
        Example:
            >>> stream = JPEGFrameStream("192.168.1.100", "12345678")
            >>> stream.connect()
            >>> for frame in stream.stream_frames():
            ...     # Process frame
            ...     with open('current_frame.jpg', 'wb') as f:
            ...         f.write(frame)
        """
        while True:
            try:
                yield self.get_frame()
            except VideoStreamError:
                break
    
    def disconnect(self):
        """Close connection to printer."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def __enter__(self):
        """Context manager support."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.disconnect()


def get_video_stream(printer_ip: str, access_code: str, printer_model: str):
    """
    Get appropriate video stream handler for printer model.
    
    Args:
        printer_ip: IP address of printer
        access_code: Printer access code
        printer_model: Model name (e.g., "X1C", "P1P", "A1")
        
    Returns:
        RTSPStream for X1 series, JPEGFrameStream for A1/P1 series
        
    Example:
        >>> stream = get_video_stream("192.168.1.100", "12345678", "P1P")
        >>> if isinstance(stream, JPEGFrameStream):
        ...     stream.connect()
        ...     frame = stream.get_frame()
    """
    model_upper = printer_model.upper()
    
    if 'X1' in model_upper:
        return RTSPStream(printer_ip, access_code)
    elif any(x in model_upper for x in ['A1', 'P1']):
        return JPEGFrameStream(printer_ip, access_code)
    else:
        # Default to JPEG stream
        return JPEGFrameStream(printer_ip, access_code)
