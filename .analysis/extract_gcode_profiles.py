#!/usr/bin/env python3
"""
G-code Profile Extractor
=========================

Extracts G-code configuration data from Bambu Studio router JavaScript files
and organizes them by printer model into separate files.

Usage:
    python extract_gcode_profiles.py <router_file.js>
"""

import re
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


def extract_gcode_sections(js_content: str) -> List[Dict[str, Any]]:
    """
    Extract G-code profile sections from JavaScript content.
    
    Returns list of dictionaries containing printer configs with G-code.
    """
    profiles = []
    
    gcode_pattern = r'(\w+_gcode):\s*`([^`]*)`'
    printer_model_pattern = r'printer_model:\s*"([^"]+)"'
    printer_name_pattern = r'name:\s*"([^"]+)"'
    setting_id_pattern = r'setting_id:\s*"([^"]+)"'
    machine_sections = re.split(r'\{type:"machine"', js_content)
    
    for idx, section in enumerate(machine_sections[1:], 1):  # Skip first split
        chunk = section[:50000]  # Reasonable size for a config object
        
        printer_model_match = re.search(printer_model_pattern, chunk)
        printer_name_match = re.search(printer_name_pattern, chunk)
        setting_id_match = re.search(setting_id_pattern, chunk)
        
        gcode_fields = {}
        for match in re.finditer(gcode_pattern, chunk, re.MULTILINE | re.DOTALL):
            field_name = match.group(1)
            gcode_content = match.group(2)
            gcode_fields[field_name] = gcode_content
        
        if gcode_fields:
            profile = {
                'printer_model': printer_model_match.group(1) if printer_model_match else f'Unknown_{idx}',
                'printer_name': printer_name_match.group(1) if printer_name_match else None,
                'setting_id': setting_id_match.group(1) if setting_id_match else None,
                'gcode': gcode_fields
            }
            profiles.append(profile)
    
    return profiles


def sanitize_filename(name: str) -> str:
    """Convert printer name to valid filename."""
    # Remove or replace invalid characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '_', name)
    return name.lower()


def save_profiles(profiles: List[Dict[str, Any]], output_dir: Path):
    """
    Save extracted G-code profiles to organized files.
    
    Creates:
    - gcode_profiles/<printer_name>.json
    - gcode_profiles/<printer_name>.gcode (for each gcode type)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    grouped = {}
    for profile in profiles:
        model = profile['printer_model']
        if model not in grouped:
            grouped[model] = []
        grouped[model].append(profile)
    
    # Save each printer's profiles
    for printer_model, printer_profiles in grouped.items():
        safe_name = sanitize_filename(printer_model)
        printer_dir = output_dir / safe_name
        printer_dir.mkdir(exist_ok=True)
        
        # Save metadata JSON
        metadata = []
        for idx, profile in enumerate(printer_profiles):
            profile_name = profile.get('printer_name') or f"{printer_model}_{idx}"
            safe_profile_name = sanitize_filename(profile_name)
            
            # Save individual G-code files
            for gcode_type, gcode_content in profile['gcode'].items():
                gcode_file = printer_dir / f"{safe_profile_name}_{gcode_type}.gcode"
                with open(gcode_file, 'w', encoding='utf-8') as f:
                    f.write(gcode_content)
            
            metadata.append({
                'printer_name': profile.get('printer_name'),
                'setting_id': profile.get('setting_id'),
                'gcode_files': list(profile['gcode'].keys())
            })
        
        # Save metadata
        metadata_file = printer_dir / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'printer_model': printer_model,
                'profiles': metadata
            }, f, indent=2)
        
        print(f"Saved {len(printer_profiles)} profile(s) for {printer_model}")
    
    # Create index file
    index = {
        'total_printers': len(grouped),
        'printers': {
            model: {
                'profile_count': len(profiles),
                'directory': sanitize_filename(model)
            }
            for model, profiles in grouped.items()
        }
    }
    
    index_file = output_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print(f"\nTotal: {len(grouped)} printer models, {len(profiles)} profiles")
    print(f"Output directory: {output_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_gcode_profiles.py <router_file.js>")
        print("\nExample:")
        print("  python extract_gcode_profiles.py analysis/router-B9dfDEf1.js")
        sys.exit(1)
    
    router_file = Path(sys.argv[1])
    
    if not router_file.exists():
        print(f"Error: File not found: {router_file}")
        sys.exit(1)
    
    print(f"Reading {router_file}...")
    with open(router_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("Extracting G-code profiles...")
    profiles = extract_gcode_sections(content)
    
    if not profiles:
        print("No G-code profiles found!")
        sys.exit(1)
    
    # Output to gcode_profiles directory
    output_dir = router_file.parent / 'gcode_profiles'
    save_profiles(profiles, output_dir)


if __name__ == '__main__':
    main()
