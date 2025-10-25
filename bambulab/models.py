"""
Data Models
===========

Data classes and models for Bambu Lab devices and status.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class Device:
    """Represents a Bambu Lab 3D printer device"""
    
    dev_id: str
    name: str
    online: bool
    print_status: str
    dev_model_name: str
    dev_product_name: str
    dev_access_code: str
    nozzle_diameter: float
    dev_structure: str
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """Create Device from API response dictionary"""
        return cls(
            dev_id=data.get('dev_id', ''),
            name=data.get('name', 'Unknown'),
            online=data.get('online', False),
            print_status=data.get('print_status', 'UNKNOWN'),
            dev_model_name=data.get('dev_model_name', ''),
            dev_product_name=data.get('dev_product_name', ''),
            dev_access_code=data.get('dev_access_code', ''),
            nozzle_diameter=data.get('nozzle_diameter', 0.4),
            dev_structure=data.get('dev_structure', ''),
            raw_data=data
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Device to dictionary"""
        return {
            'dev_id': self.dev_id,
            'name': self.name,
            'online': self.online,
            'print_status': self.print_status,
            'dev_model_name': self.dev_model_name,
            'dev_product_name': self.dev_product_name,
            'dev_access_code': self.dev_access_code,
            'nozzle_diameter': self.nozzle_diameter,
            'dev_structure': self.dev_structure,
        }


@dataclass
class PrinterStatus:
    """Represents current printer status from MQTT"""
    
    device_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Temperatures
    nozzle_temp: Optional[float] = None
    nozzle_target_temp: Optional[float] = None
    bed_temp: Optional[float] = None
    bed_target_temp: Optional[float] = None
    chamber_temp: Optional[float] = None
    
    # Speeds
    cooling_fan_speed: Optional[int] = None
    aux_fan_speed: Optional[int] = None
    chamber_fan_speed: Optional[int] = None
    
    # Print progress
    print_percentage: Optional[int] = None
    print_stage: Optional[str] = None
    remaining_time: Optional[int] = None
    layer_num: Optional[int] = None
    total_layers: Optional[int] = None
    
    # Positions
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    z_pos: Optional[float] = None
    
    # Filament
    ams_status: Optional[List[Dict]] = field(default_factory=list)
    
    # Raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_mqtt(cls, device_id: str, data: Dict[str, Any]) -> 'PrinterStatus':
        """Create PrinterStatus from MQTT message"""
        print_data = data.get('print', {})
        
        return cls(
            device_id=device_id,
            nozzle_temp=print_data.get('nozzle_temper'),
            nozzle_target_temp=print_data.get('nozzle_target_temper'),
            bed_temp=print_data.get('bed_temper'),
            bed_target_temp=print_data.get('bed_target_temper'),
            chamber_temp=print_data.get('chamber_temper'),
            cooling_fan_speed=print_data.get('cooling_fan_speed'),
            aux_fan_speed=print_data.get('aux_part_fan'),
            chamber_fan_speed=print_data.get('chamber_fan'),
            print_percentage=print_data.get('mc_percent'),
            print_stage=print_data.get('gcode_state'),
            remaining_time=print_data.get('mc_remaining_time'),
            layer_num=print_data.get('layer_num'),
            total_layers=print_data.get('total_layer_num'),
            x_pos=print_data.get('stg_cur'),
            ams_status=data.get('ams', {}).get('ams', []),
            raw_data=data
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PrinterStatus to dictionary"""
        return {
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'temperatures': {
                'nozzle': self.nozzle_temp,
                'nozzle_target': self.nozzle_target_temp,
                'bed': self.bed_temp,
                'bed_target': self.bed_target_temp,
                'chamber': self.chamber_temp,
            },
            'fans': {
                'cooling': self.cooling_fan_speed,
                'aux': self.aux_fan_speed,
                'chamber': self.chamber_fan_speed,
            },
            'progress': {
                'percentage': self.print_percentage,
                'stage': self.print_stage,
                'remaining_time': self.remaining_time,
                'layer': self.layer_num,
                'total_layers': self.total_layers,
            }
        }


@dataclass
class Project:
    """Represents a Bambu Lab project"""
    
    id: str
    name: str
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project from API response"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', 'Unnamed'),
            created=data.get('created'),
            modified=data.get('modified'),
            raw_data=data
        )
