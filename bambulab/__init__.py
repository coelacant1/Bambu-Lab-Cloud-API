"""
Bambu Lab API Library
=====================

A unified Python library for interacting with Bambu Lab 3D printers via Cloud API and MQTT.

Modules:
    client: HTTP API client for Bambu Lab Cloud API
    mqtt: MQTT client wrapper for real-time printer monitoring
    auth: Authentication and token management
    models: Data models for devices, status, etc.
    utils: Common utility functions
    video: Video/webcam streaming support

Example usage:

    from bambulab import BambuClient, MQTTClient
    
    # HTTP API
    client = BambuClient(token="your_token")
    devices = client.get_devices()
    
    # MQTT monitoring
    mqtt = MQTTClient(username="uid", token="token", device_id="serial")
    mqtt.connect()
    mqtt.subscribe_to_updates()
    
    # Video streaming
    from bambulab import get_video_stream
    stream = get_video_stream("192.168.1.100", "access_code", "P1P")

"""

__version__ = "1.0.0"
__author__ = "Coela"

from .client import BambuClient, BambuAPIError
from .mqtt import MQTTClient, MQTTBridge
from .auth import TokenManager
from .models import Device, PrinterStatus
from .utils import format_timestamp, parse_device_data
from .video import RTSPStream, JPEGFrameStream, VideoStreamError, get_video_stream
from .local_api import LocalFTPClient, LocalPrintClient, LocalAPIError, upload_and_print

__all__ = [
    'BambuClient',
    'BambuAPIError',
    'MQTTClient',
    'MQTTBridge',
    'TokenManager',
    'Device',
    'PrinterStatus',
    'format_timestamp',
    'parse_device_data',
    'RTSPStream',
    'JPEGFrameStream',
    'VideoStreamError',
    'get_video_stream',
    'LocalFTPClient',
    'LocalPrintClient',
    'LocalAPIError',
    'upload_and_print',
]
