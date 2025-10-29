# Bambu Lab Cloud API - AMS & Filament

**Last Updated:** 2025-10-25

This document covers AMS (Automatic Material System) unit data, filament information, colors, and real-time monitoring.

---

## Base URLs

**Global:** https://api.bambulab.com  
**China:** https://api.bambulab.cn  
**MQTT US:** us.mqtt.bambulab.com:8883  
**MQTT CN:** cn.mqtt.bambulab.com:8883

**Authentication:** Bearer Token (see [API_AUTHENTICATION.md](API_AUTHENTICATION.md))

---

### AMS & Filament Information

#### Overview

AMS (Automatic Material System) provides automatic multi-material printing with up to 16 filament spools (4 AMS units × 4 trays each).

Get detailed information about your AMS units, loaded filaments, temperatures, humidity levels, and remaining material.

#### Get AMS Filaments

AMS data is embedded in the device bind response. Use `get_ams_filaments(device_id)` from the Python client.

```python
from bambulab import BambuClient

client = BambuClient("YOUR_TOKEN")

# Get AMS and filament information
ams_info = client.get_ams_filaments("01234567890ABCD")

print(f"Has AMS: {ams_info['has_ams']}")
print(f"Total Trays: {ams_info['total_trays']}")

# List all units and filaments
for unit in ams_info['ams_units']:
    print(f"\nAMS Unit {unit['unit_id']}:")
    print(f"  Software: {unit['sw_version']}")
    print(f"  Hardware: {unit['hw_version']}")
    print(f"  Temperature: {unit['temperature']}C")
    print(f"  Humidity: {unit['humidity']}")
    
    for tray in unit['trays']:
        print(f"\n  Tray {tray['tray_id']}:")
        print(f"    Type: {tray['filament_type']}")
        print(f"    Color: {tray['filament_color']}")
        print(f"    Temp Range: {tray.get('nozzle_temp_min')}-{tray.get('nozzle_temp_max')}C")
        print(f"    Remaining: {tray.get('remaining')}mm")
```

#### Response Structure

```json
{
  "device_id": "01234567890ABCD",
  "has_ams": true,
  "total_trays": 4,
  "ams_units": [
    {
      "unit_id": 0,
      "software_version": "01.01.01.01",
      "hardware_version": "AMS08",
      "tray_count": 4,
      "temperature": "25.0",
      "humidity": "3",
      "humidity_raw": "28",
      "dry_time": 0,
      "info": "1001",
      "trays": [
        {
          "tray_id": 0,
          "tray_type": "Empty",
          "state": 0
        },
        {
          "tray_id": 1,
          "state": 3,
          "filament_type": "PETG-CF",
          "filament_color": "000000FF",
          "tray_info_idx": "GFG50",
          "nozzle_temp_min": 240,
          "nozzle_temp_max": 270,
          "bed_temp": "0",
          "bed_temp_type": "0",
          "tray_weight": "0",
          "tray_diameter": "0.00",
          "tray_temp": "0",
          "tray_time": "0",
          "total_len": 012345,
          "remain": -1,
          "k": 0.04,
          "n": 1,
          "cali_idx": -1,
          "tag_uid": "0000000000000000",
          "tray_id_name": "",
          "tray_sub_brands": "",
          "tray_uuid": "01234567890ABCDEF01234567890ABCD",
          "xcam_info": "01234567890ABCDEF0123456",
          "ctype": 0,
          "cols": ["000000FF"]
        },
        {
          "tray_id": 2,
          "tray_type": "Empty",
          "state": 0
        },
        {
          "tray_id": 3,
          "tray_type": "Empty",
          "state": 0
        }
      ]
    }
  ],
  "external_spool": {
    "tray_id": 254,
    "filament_type": "PETG",
    "filament_color": "FFFF00FF",
    "tray_info_idx": "GFG60",
    "nozzle_temp_min": 220,
    "nozzle_temp_max": 270,
    "remain": 0,
    "k": 0.02,
    "n": 1,
    "cali_idx": -1
  }
}
```

#### Field Descriptions

**AMS Unit Fields:**
- `unit_id`: AMS unit number (0-3)
- `software_version`: AMS firmware version
- `hardware_version`: AMS hardware model (e.g., "AMS08")
- `tray_count`: Number of trays in this unit (typically 4)
- `temperature`: Current AMS temperature (C)
- `humidity`: Humidity level index (0-5, lower is drier)
- `humidity_raw`: Raw humidity percentage
- `dry_time`: Time spent in drying mode (seconds)
- `info`: Status bits (binary flags)

**Tray Fields:**
- `tray_id`: Tray slot (0-3 per unit, or 254 for external spool)
- `state`: Tray state (0=empty, 1=loading, 2=loaded, 3=ready)
- `filament_type`: Material type (PLA, PETG, ABS, TPU, PA, PC, etc.)
- `filament_color`: RGBA hex color code
- `tray_info_idx`: Bambu Lab filament profile ID
- `nozzle_temp_min`: Minimum nozzle temperature (C)
- `nozzle_temp_max`: Maximum nozzle temperature (C)
- `bed_temp`: Bed temperature setting (C)
- `tray_weight`: Filament weight (grams)
- `tray_diameter`: Filament diameter (mm, typically 1.75)
- `total_len`: Total filament length (mm)
- `remain`: Remaining filament length (mm, -1 if unknown)
- `k`, `n`: Flow rate calibration values
- `cali_idx`: Calibration index
- `tag_uid`: RFID tag UID (if present)
- `tray_id_name`: Custom tray name
- `tray_sub_brands`: Sub-brand identifier
- `tray_uuid`: Unique tray identifier
- `xcam_info`: X-Cam color detection data
- `ctype`: Color type
- `cols`: Array of color values

**External Spool (Virtual Tray):**
- `tray_id`: Always 254
- Same fields as regular trays
- Represents filament loaded directly on printer (not in AMS)

#### Filament Types

Common filament types returned:
- **PLA** - Standard PLA
- **PLA-CF** - Carbon Fiber PLA
- **PETG** - PETG
- **PETG-CF** - Carbon Fiber PETG
- **ABS** - ABS
- **ASA** - ASA
- **TPU** - TPU (flexible)
- **PA** - Nylon (Polyamide)
- **PA-CF** - Carbon Fiber Nylon
- **PC** - Polycarbonate
- **PVA** - Support material (water-soluble)
- **GENERIC** - Unknown/generic

#### Color Codes

Colors are returned as RGBA hex strings (8 characters):
- `FF0000FF` = Red
- `00FF00FF` = Green
- `0000FFFF` = Blue
- `FFFFFFFF` = White
- `000000FF` = Black
- Last 2 digits = Alpha (FF = opaque)

Convert to display format:

```python
color_hex = "FF0000FF"
rgb = color_hex[:6]  # "FF0000"
alpha = color_hex[6:]  # "FF"
print(f"Color: #{rgb} (Alpha: {alpha})")
```

#### Python Examples

**Example 1: Check Filament Levels**

```python
def check_filament_levels(device_id):
    """Check which trays need refilling"""
    ams_info = client.get_ams_filaments(device_id)
    
    if not ams_info['has_ams']:
        print("No AMS installed")
        return
    
    low_filament = []
    
    for unit in ams_info['ams_units']:
        for tray in unit['trays']:
            remaining = tray.get('remain', 0)
            total = tray.get('total_len', 012345)
            
            if remaining > 0 and total > 0:
                percent = (remaining / total) * 100
                
                if percent < 20:
                    low_filament.append({
                        'unit': unit['unit_id'],
                        'tray': tray['tray_id'],
                        'type': tray.get('filament_type', 'Unknown'),
                        'remaining': f"{percent:.1f}%"
                    })
    
    if low_filament:
        print("Low filament levels:")
        for item in low_filament:
            print(f"  Unit {item['unit']} Tray {item['tray']}: "
                  f"{item['type']} - {item['remaining']} remaining")
    else:
        print("All filaments OK")

check_filament_levels("01234567890ABCD")
```

**Example 2: List All Filaments**

```python
def list_all_filaments(device_id):
    """List all loaded filaments with details"""
    ams_info = client.get_ams_filaments(device_id)
    
    if not ams_info['has_ams']:
        print("No AMS installed")
        return
    
    print(f"Total Trays: {ams_info['total_trays']}\n")
    
    for unit in ams_info['ams_units']:
        print(f"AMS Unit {unit['unit_id']} (v{unit['software_version']})")
        print(f"  Temperature: {unit['temperature']}C")
        print(f"  Humidity: Level {unit['humidity']}")
        print("-" * 50)
        
        for tray in unit['trays']:
            if tray.get('state', 0) == 0:
                print(f"  Tray {tray['tray_id']}: Empty")
                continue
                
            # Convert hex color to readable format
            color = tray.get('filament_color', 'N/A')
            if color != 'N/A' and len(color) >= 6:
                color = f"#{color[:6]}"
            
            print(f"  Tray {tray['tray_id']}:")
            print(f"    Material: {tray.get('filament_type', 'Unknown')}")
            print(f"    Color: {color}")
            temp_min = tray.get('nozzle_temp_min', 'N/A')
            temp_max = tray.get('nozzle_temp_max', 'N/A')
            print(f"    Nozzle Temp: {temp_min}-{temp_max}C")
            
            remaining = tray.get('remain', -1)
            total = tray.get('total_len', 0)
            if remaining > 0 and total > 0:
                percent = (remaining / total) * 100
                print(f"    Remaining: {remaining}mm ({percent:.1f}%)")
            print()

list_all_filaments("01234567890ABCD")
```

**Example 3: Monitor AMS Temperature/Humidity**

```python
def monitor_ams_environment(device_id):
    """Monitor AMS environmental conditions"""
    ams_info = client.get_ams_filaments(device_id)
    
    if not ams_info['has_ams']:
        print("No AMS installed")
        return
    
    for unit in ams_info['ams_units']:
        temp = float(unit['temperature'])
        humidity_idx = int(unit['humidity'])
        humidity_raw = int(unit['humidity_raw'])
        
        print(f"AMS Unit {unit['unit_id']}:")
        print(f"  Temperature: {temp}C")
        print(f"  Humidity: Level {humidity_idx} ({humidity_raw}%)")
        
        # Check conditions
        if temp > 35:
            print("  WARNING: High temperature")
        if humidity_idx > 3:
            print("  WARNING: High humidity - consider drying")
        print()

monitor_ams_environment("01234567890ABCD")
```

#### Real-Time Updates via MQTT

**Note:** The `get_ams_filaments()` method returns static data from the device bind endpoint.

For **real-time AMS updates** (during printing, filament changes), use MQTT:

```python
from bambulab import MQTTClient

mqtt = MQTTClient(
    username="bblp",
    token="your_token",
    device_id="01234567890ABCD"
)

def on_message(data):
    if 'ams' in data.get('print', {}):
        ams_data = data['print']['ams']
        
        # Real-time AMS data
        for unit in ams_data.get('ams', []):
            unit_id = unit.get('id', 0)
            temp = unit.get('temp', 'N/A')
            humidity = unit.get('humidity', 'N/A')
            
            print(f"AMS Unit {unit_id}: {temp}C, Humidity {humidity}%")
            
            for tray in unit.get('tray', []):
                tray_id = tray.get('id', 0)
                remain = tray.get('remain', -1)
                
                if remain > 0:
                    print(f"  Tray {tray_id}: {remain}mm remaining")

mqtt.connect()
mqtt.subscribe_to_updates(on_message)

# Keep running for real-time updates
try:
    while True:
        time.sleep(1)
finally:
    mqtt.disconnect()
```

#### Without AMS

If printer doesn't have AMS, the response will be:

```json
{
  "device_id": "01234567890ABCD",
  "has_ams": false,
  "total_trays": 0,
  "ams_units": [],
  "external_spool": {
    "tray_id": 254,
    "filament_type": "PLA",
    "filament_color": "FFFFFFFF",
    "remain": 0
  }
}
```

#### Limitations

- **Static snapshot** - Not updated in real-time (use MQTT for that)
- **AMS required** - Only works if printer has AMS installed
- **May be empty** - Some printers may not report detailed tray data
- **Field names vary** - Different firmware versions may use different field names
- **Remaining inaccurate** - `remain` field may be -1 or 0 if not tracked

---


---

## See Also

- [API_DEVICES.md](API_DEVICES.md) - Device management
- [API_MQTT.md](API_MQTT.md) - MQTT protocol for real-time AMS updates
- [API_REFERENCE.md](API_REFERENCE.md) - Error codes
- [API_AUTHENTICATION.md](API_AUTHENTICATION.md) - Authentication
