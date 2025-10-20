"""
Bambu Lab MQTT Client
=====================

MQTT client wrapper for real-time printer monitoring and control.
"""

import json
import ssl
import threading
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

logger = logging.getLogger(__name__)


class MQTTError(Exception):
    """Base exception for MQTT errors"""
    pass


class MQTTClient:
    """
    MQTT client for monitoring Bambu Lab printers.
    
    Connects to Bambu Lab cloud MQTT broker and subscribes to device updates.
    """
    
    BROKER = "us.mqtt.bambulab.com"
    PORT = 8883
    
    def __init__(
        self,
        username: str,
        access_token: str,
        device_id: str,
        on_message: Optional[Callable] = None
    ):
        """
        Initialize MQTT client.
        
        Args:
            username: User UID
            access_token: Bambu Lab access token
            device_id: Device serial number to monitor
            on_message: Optional callback for messages (receives device_id, data)
        """
        if mqtt is None:
            raise MQTTError("paho-mqtt library not installed. Install with: pip install paho-mqtt")
        
        self.username = username
        self.access_token = access_token
        self.device_id = device_id
        self.on_message_callback = on_message
        
        self.client = None
        self.connected = False
        self.message_count = 0
        self.last_data = {}
        
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker: {self.BROKER}")
            
            # Subscribe to device report topic
            topic = f"device/{self.device_id}/report"
            client.subscribe(topic)
            logger.info(f"Subscribed to: {topic}")
        else:
            logger.error(f"Connection failed with code {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc, properties=None, reason_code=None):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnect (code {rc})")
    
    def _on_message(self, client, userdata, msg, properties=None):
        """Callback when message received"""
        self.message_count += 1
        
        try:
            data = json.loads(msg.payload.decode('utf-8'))
            self.last_data = data
            
            # Call user callback if provided
            if self.on_message_callback:
                self.on_message_callback(self.device_id, data)
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message from {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def connect(self, blocking: bool = False):
        """
        Connect to MQTT broker.
        
        Args:
            blocking: If True, run blocking loop. If False, start background thread.
        """
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"bambu-client-{self.device_id}"
        )
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set authentication - username must be prefixed with "u_"
        mqtt_username = self.username if self.username.startswith('u_') else f"u_{self.username}"
        self.client.username_pw_set(mqtt_username, self.access_token)
        
        # Configure TLS
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        
        # Connect
        logger.info(f"Connecting to {self.BROKER}:{self.PORT}...")
        self.client.connect(self.BROKER, self.PORT, keepalive=60)
        
        if blocking:
            self.client.loop_forever()
        else:
            self.client.loop_start()
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")
    
    def publish(self, command: Dict):
        """
        Publish command to device.
        
        Args:
            command: Command dictionary to send
        """
        if not self.connected:
            raise MQTTError("Not connected to broker")
        
        topic = f"device/{self.device_id}/request"
        payload = json.dumps(command)
        self.client.publish(topic, payload)
        logger.info(f"Published command to {topic}")
    
    def request_full_status(self):
        """
        Request complete printer status via pushall command.
        
        Sends a "pushall" command to the printer to request a complete
        status dump with all sensor data, temperatures, positions, etc.
        
        The response will be received via the on_message callback.
        
        Example:
            client.connect()
            client.request_full_status()
            # Wait for message via callback
        """
        command = {
            "pushing": {
                "command": "pushall"
            }
        }
        self.publish(command)
        logger.info("Requested full printer status (pushall)")
    
    def get_last_data(self) -> Dict:
        """Get the most recent data received"""
        return self.last_data.copy()


class MQTTBridge:
    """
    MQTT bridge for compatibility layer.
    
    Bridges cloud MQTT to local MQTT broker for legacy clients.
    """
    
    def __init__(
        self,
        username: str,
        access_token: str,
        devices: List[Dict],
        local_port: int = 1883
    ):
        """
        Initialize MQTT bridge.
        
        Args:
            username: User UID
            access_token: Bambu Lab access token
            devices: List of device dictionaries with device_id and access_code
            local_port: Local MQTT broker port
        """
        if mqtt is None:
            raise MQTTError("paho-mqtt library not installed")
        
        self.username = username
        self.access_token = access_token
        self.devices = devices
        self.local_port = local_port
        
        self.cloud_clients = {}
        self.local_broker = None
        self.message_cache = {}
        
    def start(self):
        """Start the MQTT bridge"""
        logger.info("Starting MQTT bridge...")
        
        # Create cloud MQTT client for each device
        for device in self.devices:
            device_id = device['device_id']
            
            def make_callback(dev_id):
                return lambda device_id, data: self._forward_to_local(dev_id, data)
            
            client = MQTTClient(
                username=self.username,
                access_token=self.access_token,
                device_id=device_id,
                on_message=make_callback(device_id)
            )
            
            client.connect(blocking=False)
            self.cloud_clients[device_id] = client
            logger.info(f"Bridge connected for device: {device_id}")
    
    def stop(self):
        """Stop the MQTT bridge"""
        logger.info("Stopping MQTT bridge...")
        for client in self.cloud_clients.values():
            client.disconnect()
        self.cloud_clients.clear()
    
    def _forward_to_local(self, device_id: str, data: Dict):
        """Forward cloud message to local broker"""
        self.message_cache[device_id] = data
        logger.debug(f"Cached message for device {device_id}")
        # Note: Actual local MQTT broker implementation would go here
    
    def get_cached_data(self, device_id: str) -> Optional[Dict]:
        """Get cached data for a device"""
        return self.message_cache.get(device_id)
