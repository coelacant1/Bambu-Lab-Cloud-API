# Bambu Lab Cloud API - MQTT Protocol

**Last Updated:** 2025-10-25

This document covers MQTT connection, topics, message formats, device commands, and real-time monitoring.

---

## MQTT Brokers

**US Broker:** us.mqtt.bambulab.com:8883  
**China Broker:** cn.mqtt.bambulab.com:8883  
**Dev Broker:** dev.mqtt.bambu-lab.com:8883

**Protocol:** MQTT over TLS (port 8883)  
**Authentication:** Username (user ID) + Password (access code)

---

## MQTT PROTOCOL

### Connection

```
Broker:   us.mqtt.bambulab.com
Port:     8883 (TLS)
Protocol: MQTT 3.1.1 / 5.0

Authentication:
- Username: <user_id>
- Password: <mqtt_token>
- TLS: Required
```

### Topic Structure

**Subscribe to device updates:**
```
device/<device_id>/report
device/<device_id>/status
printer/<device_id>/state
```

**Publish commands:**
```
device/<device_id>/request
printer/<device_id>/command
```

### Message Format

**Print Commands:**
```json
{
  "print": {
    "command": "start|pause|stop|resume",
    "sequence_id": "12345",
    "param": {
      "file_url": "https://...",
      "file_name": "model.3mf"
    }
  }
}
```

**Request Full Status (pushall):**
```json
{
  "pushing": {
    "command": "pushall"
  }
}
```

This command requests the printer to send a complete status dump including all sensor data, temperatures, positions, AMS status, and current print job information. The response is received on the `device/<device_id>/report` topic.

### MQTT Status Response Structure

When you subscribe to `device/<device_id>/report` or request full status with `pushall`, the printer sends comprehensive status data.

**Full Status Message Structure:**

The response is a nested JSON with a `print` object containing 60+ fields:

```json
{
  "print": {
    // Temperatures
    "nozzle_temper": 23.625,
    "nozzle_target_temper": 0,
    "bed_temper": 20.71875,
    "bed_target_temper": 0,
    "chamber_temper": 5,
    
    // Print Progress
    "gcode_state": "IDLE|RUNNING|PAUSE|FAILED|FINISH",
    "mc_percent": 45,
    "mc_remaining_time": 3600,
    "layer_num": 125,
    "total_layer_num": 250,
    
    // Print Job Info
    "subtask_name": "model.3mf",
    "project_id": "012345678",
    "profile_id": "012345678",
    "task_id": "012345678",
    "subtask_id": "012345678",
    "gcode_file": "cache/012345678.gcode",
    
    // Fan Speeds (0-15 scale)
    "heatbreak_fan_speed": "0",
    "cooling_fan_speed": "0",
    "big_fan1_speed": "0",
    "big_fan2_speed": "0",
    "fan_gear": 0,
    
    // Speed Settings
    "spd_mag": 100,
    "spd_lvl": 2,
    
    // Print Stage
    "mc_print_stage": "0-20",
    "mc_print_sub_stage": 0,
    "print_type": "idle|cloud_file|local",
    "stg": [],
    "stg_cur": 255,
    
    // Hardware Info
    "nozzle_diameter": "0.4",
    "nozzle_type": "stainless_steel|hardened_steel",
    "lifecycle": "product",
    "wifi_signal": "-45dBm",
    
    // Errors & Status
    "print_error": 0,
    "hms": [
      {
        "attr": 01234567,
        "code": 65543,
        "action": 0,
        "timestamp": 1761352945
      }
    ],
    
    // AMS (Automatic Material System)
    "ams": {
      "ams": [
        {
          "id": "0",
          "humidity": "3",
          "humidity_raw": "28",
          "temp": "25.0",
          "tray": [
            {
              "id": "0",
              "tray_type": "PLA",
              "tray_color": "FF0000FF",
              "nozzle_temp_min": "190",
              "nozzle_temp_max": "230",
              "remain": 750
            }
          ]
        }
      ],
      "ams_exist_bits": "1",
      "tray_exist_bits": "2",
      "tray_now": "255",
      "version": 2
    },
    
    // External Spool (Virtual Tray)
    "vt_tray": {
      "id": "254",
      "tray_type": "PETG",
      "tray_color": "FFFF00FF",
      "remain": 0
    },
    
    // Camera & Lighting
    "ipcam": {
      "ipcam_dev": "1",
      "ipcam_record": "enable",
      "timelapse": "disable",
      "resolution": "1920x1080",
      "tutk_server": "disable"
    },
    "lights_report": [
      {
        "node": "chamber_light",
        "mode": "on|off"
      }
    ],
    
    // Network
    "net": {
      "conf": 0,
      "info": [
        {
          "ip": 3389106368,
          "mask": 01234567
        }
      ]
    },
    
    // Firmware Updates
    "upgrade_state": {
      "status": "IDLE|UPGRADING",
      "progress": "",
      "new_ver_list": [
        {
          "name": "ota",
          "cur_ver": "01.01.01.01",
          "new_ver": "01.01.01.01"
        }
      ]
    },
    
    // Command Info
    "command": "push_status",
    "msg": 0,
    "sequence_id": "1628"
  }
}
```

**Key Field Categories:**

| Category | Fields | Description |
|----------|--------|-------------|
| **Temperatures** | `nozzle_temper`, `bed_temper`, `chamber_temper` | Current temperatures in C |
| **Progress** | `mc_percent`, `layer_num`, `mc_remaining_time` | Print progress info |
| **State** | `gcode_state`, `mc_print_stage`, `print_type` | Current printer state |
| **Speeds** | Fan speeds, `spd_mag`, `spd_lvl` | Fan speeds and print speed |
| **AMS** | `ams`, `vt_tray` | Filament system status |
| **Hardware** | `nozzle_diameter`, `nozzle_type`, `wifi_signal` | Hardware specs |
| **Errors** | `print_error`, `hms` | Error codes and HMS messages |
| **Camera** | `ipcam`, `lights_report` | Camera and lighting status |

**Update Frequency:**
- Status messages typically sent every 0.5-2 seconds
- Full status on connection or when `pushall` requested
- Frequency increases during active printing

---


---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management
- [API_AMS_FILAMENT.md](API_AMS_FILAMENT.md) - AMS data via MQTT
- [API_CAMERA.md](API_CAMERA.md) - Camera streaming
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
