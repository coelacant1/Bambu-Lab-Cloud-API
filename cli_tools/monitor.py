#!/usr/bin/env python3
"""
Monitor Bambu Lab Printers via MQTT
====================================

Real-time monitoring of printer status, temperatures, and progress using MQTT.
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for bambulab import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import MQTTClient, PrinterStatus
from bambulab.utils import format_temperature, format_percentage, format_time_remaining


class PrinterMonitor:
    """Monitor printer status with formatted output"""
    
    def __init__(self, username: str, access_token: str, device_id: str):
        self.device_id = device_id
        self.message_count = 0
        self.last_update = None
        
        # Create MQTT client with callback
        self.client = MQTTClient(
            username=username,
            access_token=access_token,
            device_id=device_id,
            on_message=self.on_message
        )
    
    def on_message(self, device_id: str, data: dict):
        """Handle incoming MQTT messages"""
        self.message_count += 1
        self.last_update = datetime.now()
        
        # Parse status
        status = PrinterStatus.from_mqtt(device_id, data)
        
        # Display update
        self.display_status(status)
    
    def display_status(self, status: PrinterStatus):
        """Display printer status in formatted output"""
        timestamp = status.timestamp.strftime("%H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"Update #{self.message_count} - {timestamp}")
        print(f"{'='*80}")
        
        # Basic info
        print(f"\nDevice: {self.device_id}")
        
        # Temperatures
        print(f"\nTemperatures:")
        print(f"  Nozzle:  {format_temperature(status.nozzle_temp)} -> {format_temperature(status.nozzle_target_temp)}")
        print(f"  Bed:     {format_temperature(status.bed_temp)} -> {format_temperature(status.bed_target_temp)}")
        print(f"  Chamber: {format_temperature(status.chamber_temp)}")
        
        # Print progress
        if status.print_stage:
            print(f"\nPrint Status:")
            print(f"  Stage:     {status.print_stage}")
            print(f"  Progress:  {format_percentage(status.print_percentage)}")
            print(f"  Remaining: {format_time_remaining(status.remaining_time)}")
            if status.layer_num and status.total_layers:
                print(f"  Layer:     {status.layer_num}/{status.total_layers}")
        
        # Position information
        if status.x_pos is not None or status.y_pos is not None or status.z_pos is not None:
            print(f"\nPosition:")
            if status.x_pos is not None:
                print(f"  X: {status.x_pos:.2f}mm")
            if status.y_pos is not None:
                print(f"  Y: {status.y_pos:.2f}mm")
            if status.z_pos is not None:
                print(f"  Z: {status.z_pos:.2f}mm")
        
        # Fans
        if status.cooling_fan_speed is not None:
            print(f"\nFans:")
            print(f"  Cooling:  {format_percentage(status.cooling_fan_speed)}")
            if status.aux_fan_speed is not None:
                print(f"  Aux:      {format_percentage(status.aux_fan_speed)}")
            if status.chamber_fan_speed is not None:
                print(f"  Chamber:  {format_percentage(status.chamber_fan_speed)}")
        
        # AMS status
        if status.ams_status:
            print(f"\nAMS: {len(status.ams_status)} unit(s)")
            for idx, ams_unit in enumerate(status.ams_status, 1):
                print(f"  Unit {idx}:")
                if 'tray' in ams_unit:
                    trays = ams_unit['tray']
                    for tray_idx, tray in enumerate(trays):
                        if tray.get('tray_type'):
                            color = tray.get('tray_color', 'Unknown')
                            material = tray.get('tray_type', 'Unknown')
                            print(f"    Tray {tray_idx}: {material} ({color})")
        
        # Raw data summary
        print(f"\nData: {len(status.raw_data)} fields in message")
    
    def start(self):
        """Start monitoring"""
        print("=" * 80)
        print("Bambu Lab Printer Monitor")
        print("=" * 80)
        print(f"Device ID: {self.device_id}")
        print(f"Broker: {self.client.BROKER}:{self.client.PORT}")
        print()
        print("Connecting to MQTT...")
        print("=" * 80)
        
        try:
            # Connect and start monitoring
            self.client.connect(blocking=True)
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.client.disconnect()
            print(f"Total messages received: {self.message_count}")


def main():
    """Main entry point"""
    if len(sys.argv) < 4:
        print("Usage: python monitor.py <username> <access_token> <device_id> [device_id2 ...]")
        print()
        print("Arguments:")
        print("  username:      Your Bambu Lab user UID")
        print("  access_token:  Your Bambu Lab access token")
        print("  device_id:     Device serial number to monitor")
        print()
        print("Example:")
        print("  python monitor.py u_123456789 AADBD2wZe_token... 01S00A000000000")
        print()
        print("Tip: Press Ctrl+C to stop monitoring")
        sys.exit(1)
    
    username = sys.argv[1]
    access_token = sys.argv[2]
    device_ids = sys.argv[3:]
    
    if len(device_ids) == 1:
        # Single device monitoring
        monitor = PrinterMonitor(username, access_token, device_ids[0])
        monitor.start()
    else:
        # Multi-device monitoring
        print(f"Monitoring {len(device_ids)} devices...")
        print("Note: Multi-device display is simplified")
        print()
        
        def multi_callback(device_id, data):
            status = PrinterStatus.from_mqtt(device_id, data)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {device_id}: {status.print_stage} - {format_percentage(status.print_percentage)}")
        
        clients = []
        for device_id in device_ids:
            client = MQTTClient(username, access_token, device_id, on_message=multi_callback)
            client.connect(blocking=False)
            clients.append(client)
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping monitors...")
            for client in clients:
                client.disconnect()


if __name__ == '__main__':
    main()
