"""
Tests for MQTT control commands
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import json

from bambulab.mqtt import MQTTClient, MQTTError


class TestMQTTCommands(unittest.TestCase):
    """Test MQTT device control commands"""
    
    def setUp(self):
        """Set up test client with mocked MQTT"""
        with patch('bambulab.mqtt.mqtt'):
            self.client = MQTTClient(
                username="test_user",
                access_token="test_token",
                device_id="TEST123456789"
            )
            self.client.client = MagicMock()
            self.client.connected = True
    
    def test_pause_print(self):
        """Test pause print command"""
        self.client.pause_print()
        
        expected_command = {"print": {"command": "pause"}}
        self.client.client.publish.assert_called_once()
        
        args = self.client.client.publish.call_args
        self.assertEqual(args[0][0], "device/TEST123456789/request")
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_resume_print(self):
        """Test resume print command"""
        self.client.resume_print()
        
        expected_command = {"print": {"command": "resume"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_stop_print(self):
        """Test stop print command"""
        self.client.stop_print()
        
        expected_command = {"print": {"command": "stop"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_nozzle_temp(self):
        """Test set nozzle temperature command"""
        self.client.set_nozzle_temp(220)
        
        expected_command = {"print": {"command": "set_nozzle_temp", "param": "220"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_bed_temp(self):
        """Test set bed temperature command"""
        self.client.set_bed_temp(60)
        
        expected_command = {"print": {"command": "set_bed_temp", "param": "60"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_chamber_temp(self):
        """Test set chamber temperature command"""
        self.client.set_chamber_temp(35)
        
        expected_command = {"print": {"command": "set_chamber_temp", "param": "35"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_fan_speed(self):
        """Test set fan speed command"""
        self.client.set_fan_speed(75)
        
        expected_command = {"print": {"command": "set_fan_speed", "param": "75"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_fan_speed_validation(self):
        """Test fan speed validation"""
        with self.assertRaises(ValueError):
            self.client.set_fan_speed(-1)
        
        with self.assertRaises(ValueError):
            self.client.set_fan_speed(101)
    
    def test_set_airduct_fan(self):
        """Test set air duct fan command"""
        self.client.set_airduct_fan(50)
        
        expected_command = {"print": {"command": "set_airduct", "param": "50"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_airduct_fan_validation(self):
        """Test air duct fan speed validation"""
        with self.assertRaises(ValueError):
            self.client.set_airduct_fan(150)
    
    def test_set_chamber_fan(self):
        """Test set chamber fan (CTT) command"""
        self.client.set_chamber_fan(100)
        
        expected_command = {"print": {"command": "set_ctt", "param": "100"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_set_chamber_fan_validation(self):
        """Test chamber fan speed validation"""
        with self.assertRaises(ValueError):
            self.client.set_chamber_fan(-10)
    
    def test_command_when_disconnected(self):
        """Test that commands fail when not connected"""
        self.client.connected = False
        
        with self.assertRaises(MQTTError):
            self.client.pause_print()
    
    def test_request_full_status(self):
        """Test request full status command"""
        self.client.request_full_status()
        
        expected_command = {"pushing": {"command": "pushall"}}
        args = self.client.client.publish.call_args
        self.assertEqual(json.loads(args[0][1]), expected_command)
    
    def test_publish_uses_correct_topic(self):
        """Test that all commands use correct MQTT topic"""
        commands = [
            self.client.pause_print,
            self.client.resume_print,
            self.client.stop_print,
            lambda: self.client.set_nozzle_temp(200),
            lambda: self.client.set_fan_speed(50),
        ]
        
        for cmd in commands:
            self.client.client.reset_mock()
            cmd()
            args = self.client.client.publish.call_args
            self.assertEqual(args[0][0], "device/TEST123456789/request")


class TestMQTTCommandIntegration(unittest.TestCase):
    """Integration tests for MQTT commands (require actual connection)"""
    
    @unittest.skip("Requires actual MQTT broker connection")
    def test_real_pause_command(self):
        """Test sending pause command to real printer"""
        # This would require actual credentials and device
        client = MQTTClient(
            username="real_username",
            access_token="real_token",
            device_id="real_device_id"
        )
        client.connect(blocking=False)
        client.pause_print()
        client.disconnect()


if __name__ == '__main__':
    unittest.main()
