"""
Bambu Lab CLI Tools
===================

Command-line utilities for interacting with Bambu Lab printers.

Tools:
    monitor: Real-time MQTT monitoring with formatted output
    query: Query printer information from Cloud API

Usage examples:

    # Monitor printer in real-time
    python monitor.py <username> <token> <device_id>
    
    # Query printer information
    python query.py <token> --devices --status

"""

__version__ = "1.0.0"
__author__ = "Coela"
