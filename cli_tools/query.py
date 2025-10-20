#!/usr/bin/env python3
"""
Query Bambu Lab Printer Information
====================================

Query and display comprehensive printer information from the Cloud API.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for bambulab import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambulab import BambuClient, Device
from bambulab.client import BambuAPIError
from bambulab.utils import format_temperature


def display_device_info(device: Device):
    """Display device information in formatted output"""
    print(f"\n{'='*80}")
    print(f"Device: {device.name}")
    print(f"{'='*80}")
    print(f"  Serial Number:  {device.dev_id}")
    print(f"  Model:          {device.dev_product_name} ({device.dev_model_name})")
    print(f"  Structure:      {device.dev_structure}")
    print(f"  Nozzle Size:    {device.nozzle_diameter}mm")
    print(f"  Access Code:    {device.dev_access_code}")
    print(f"  Online:         {'Yes' if device.online else 'No'}")
    print(f"  Print Status:   {device.print_status}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python query.py <access_token> [options]")
        print()
        print("Arguments:")
        print("  access_token:  Your Bambu Lab access token")
        print()
        print("Options:")
        print("  --devices      Show device list (default)")
        print("  --status       Show print status")
        print("  --profile      Show user profile")
        print("  --projects     Show projects")
        print("  --firmware     Show firmware info")
        print("  --json         Output in JSON format")
        print("  --device <id>  Filter by device ID")
        print()
        print("Examples:")
        print("  python query.py AADBD2wZe_token...")
        print("  python query.py AADBD2wZe_token... --status")
        print("  python query.py AADBD2wZe_token... --device 01S00A000000000")
        sys.exit(1)
    
    access_token = sys.argv[1]
    args = sys.argv[2:]
    
    # Parse options
    show_json = '--json' in args
    show_status = '--status' in args
    show_profile = '--profile' in args
    show_projects = '--projects' in args
    show_firmware = '--firmware' in args
    
    device_filter = None
    if '--device' in args:
        idx = args.index('--device')
        if idx + 1 < len(args):
            device_filter = args[idx + 1]
    
    # Default to showing devices
    show_devices = not any([show_status, show_profile, show_projects, show_firmware])
    
    # Create API client
    try:
        client = BambuClient(access_token)
    except Exception as e:
        print(f"Error: Failed to create API client: {e}")
        sys.exit(1)
    
    print("=" * 80)
    print("Bambu Lab Printer Information Query")
    print("=" * 80)
    print()
    
    # Query devices
    if show_devices or device_filter:
        try:
            print("Fetching device list...")
            devices_data = client.get_devices()
            devices = [Device.from_dict(d) for d in devices_data]
            
            if device_filter:
                devices = [d for d in devices if d.dev_id == device_filter]
            
            if show_json:
                print(json.dumps([d.to_dict() for d in devices], indent=2))
            else:
                print(f"\nFound {len(devices)} device(s):")
                for device in devices:
                    display_device_info(device)
        
        except BambuAPIError as e:
            print(f"Error fetching devices: {e}")
            sys.exit(1)
    
    # Query print status
    if show_status:
        try:
            print("\nFetching print status...")
            status = client.get_print_status(force=True)
            
            if show_json:
                print(json.dumps(status, indent=2))
            else:
                devices = status.get('devices', [])
                print(f"\nPrint status for {len(devices)} device(s):")
                for device_status in devices:
                    if device_filter and device_status.get('dev_id') != device_filter:
                        continue
                    
                    print(f"\n{'='*80}")
                    print(f"{device_status.get('name', 'Unknown')} ({device_status.get('dev_id')})")
                    print(f"{'='*80}")
                    print(f"  Status: {device_status.get('print_status', 'Unknown')}")
                    
                    if 'print' in device_status:
                        print_data = device_status['print']
                        
                        # Progress
                        if 'mc_percent' in print_data:
                            print(f"  Progress: {print_data['mc_percent']}%")
                        if 'layer_num' in print_data and 'total_layer_num' in print_data:
                            print(f"  Layer: {print_data['layer_num']}/{print_data['total_layer_num']}")
                        if 'mc_remaining_time' in print_data:
                            remaining = print_data['mc_remaining_time']
                            hours = remaining // 60
                            minutes = remaining % 60
                            print(f"  Time Remaining: {hours}h {minutes}m")
                        
                        # Temperatures
                        print(f"\n  Temperatures:")
                        if 'nozzle_temper' in print_data:
                            target = print_data.get('nozzle_target_temper', 0)
                            print(f"    Nozzle: {print_data['nozzle_temper']}°C → {target}°C")
                        if 'bed_temper' in print_data:
                            target = print_data.get('bed_target_temper', 0)
                            print(f"    Bed: {print_data['bed_temper']}°C → {target}°C")
                        if 'chamber_temper' in print_data:
                            print(f"    Chamber: {print_data['chamber_temper']}°C")
                        
                        # Fans
                        if any(k in print_data for k in ['cooling_fan_speed', 'aux_part_fan', 'chamber_fan']):
                            print(f"\n  Fans:")
                            if 'cooling_fan_speed' in print_data:
                                print(f"    Cooling: {print_data['cooling_fan_speed']}%")
                            if 'aux_part_fan' in print_data:
                                print(f"    Aux: {print_data['aux_part_fan']}%")
                            if 'chamber_fan' in print_data:
                                print(f"    Chamber: {print_data['chamber_fan']}%")
                        
                        # File info
                        if 'gcode_file' in print_data:
                            print(f"\n  File: {print_data['gcode_file']}")
                        if 'gcode_state' in print_data:
                            print(f"  G-code State: {print_data['gcode_state']}")
        
        except BambuAPIError as e:
            print(f"Error fetching status: {e}")
            sys.exit(1)
    
    # Query user profile
    if show_profile:
        try:
            print("\nFetching user profile...")
            profile = client.get_user_profile()
            
            if show_json:
                print(json.dumps(profile, indent=2))
            else:
                print(f"\nUser Profile:")
                print(f"  UID:     {profile.get('uid', 'N/A')}")
                print(f"  Name:    {profile.get('name', 'N/A')}")
                print(f"  Account: {profile.get('account', 'N/A')}")
                if 'productModels' in profile:
                    print(f"  Printers: {', '.join(profile['productModels'])}")
        
        except BambuAPIError as e:
            print(f"Error fetching profile: {e}")
            sys.exit(1)
    
    # Query projects
    if show_projects:
        try:
            print("\nFetching projects...")
            projects = client.get_projects()
            
            if show_json:
                print(json.dumps(projects, indent=2))
            else:
                print(f"\nFound {len(projects)} project(s):")
                for project in projects:
                    print(f"\n  {project.get('name', 'Unnamed')}")
                    print(f"    ID: {project.get('id', 'N/A')}")
                    if 'created' in project:
                        print(f"    Created: {project['created']}")
        
        except BambuAPIError as e:
            print(f"Error fetching projects: {e}")
            sys.exit(1)
    
    # Query firmware
    if show_firmware and device_filter:
        try:
            print(f"\nFetching firmware info for {device_filter}...")
            firmware = client.get_device_version(device_filter)
            
            if show_json:
                print(json.dumps(firmware, indent=2))
            else:
                print(f"\nFirmware Information:")
                if 'devices' in firmware:
                    for device in firmware['devices']:
                        if device.get('dev_id') == device_filter:
                            fw = device.get('firmware', {})
                            print(f"  Current:  {fw.get('current_version', 'N/A')}")
                            print(f"  Available: {fw.get('available_version', 'N/A')}")
                            print(f"  Force Update: {fw.get('force_update', False)}")
        
        except BambuAPIError as e:
            print(f"Error fetching firmware: {e}")
            sys.exit(1)
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
