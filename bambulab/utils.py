"""
Utility Functions
=================

Common utility functions for the Bambu Lab library.
"""

from datetime import datetime
from typing import Dict, Any, Optional


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime to format (default: now)
        fmt: Format string
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def parse_device_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize device data from various sources.
    
    Args:
        data: Raw device data
        
    Returns:
        Normalized device data
    """
    # Extract print data if nested
    if 'print' in data:
        print_data = data['print']
    else:
        print_data = data
    
    return {
        'device_id': data.get('dev_id', ''),
        'name': data.get('name', 'Unknown'),
        'online': data.get('online', False),
        'print_status': print_data.get('gcode_state', 'UNKNOWN'),
        'temperatures': {
            'nozzle': print_data.get('nozzle_temper'),
            'bed': print_data.get('bed_temper'),
            'chamber': print_data.get('chamber_temper'),
        },
        'progress': print_data.get('mc_percent', 0),
    }


def format_temperature(temp: Optional[float]) -> str:
    """
    Format a temperature value.
    
    Args:
        temp: Temperature in Celsius
        
    Returns:
        Formatted temperature string
    """
    if temp is None:
        return "N/A"
    return f"{temp:.1f}°C"


def format_percentage(value: Optional[int]) -> str:
    """
    Format a percentage value.
    
    Args:
        value: Percentage (0-100)
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    return f"{value}%"


def format_time_remaining(seconds: Optional[int]) -> str:
    """
    Format remaining time in human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (e.g., "2h 34m")
    """
    if seconds is None or seconds < 0:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def safe_get(data: Dict, *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to traverse
        *keys: Keys to traverse
        default: Default value if not found
        
    Returns:
        Value at the nested key path, or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current
