"""
Bambu Lab Servers
=============================

Servers for Bambu Lab Cloud API integration

Servers:
    proxy: Token-based API proxy with multiple modes
        - strict mode: GET-only operations (port 5001)
        - full mode: Complete 1:1 proxy (port 5003)
    
    compatibility: Legacy API compatibility layer
        - Mimics old local API endpoints (port 8080)
        - MQTT bridge for real-time updates
        - Works without developer mode

Usage examples:

    # Run proxy server in strict mode
    python proxy.py strict
    
    # Run proxy server in full mode
    python proxy.py full
    
    # Run compatibility server
    python compatibility.py

"""

__version__ = "1.0.0"
__author__ = "Coela"
