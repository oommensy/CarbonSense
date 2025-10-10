"""
IoT Sensor Simulator for CarbonSense
Simulates real-time IoT sensor data for carbon footprint tracking
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass, asdict
import uuid

@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: str
    location: str
    value: float
    unit: str
    timestamp: datetime
    quality: str  # 'high', 'medium', 'low'
    battery_level: Optional[float] = None

class IoTSensorSimulator:
    """Simulates various IoT sensors for carbon footprint verification"""
    
    def __init__(self):
        self.sensors = self._initialize_sensors()
        self.readings_history = []
        
    def _initialize_sensors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize virtual IoT sensors"""
        return {
            # Home energy monitoring
            'home_energy_001': {
                'type': 'energy_meter',
                'location': 'Main electrical panel',
                'baseline': 3.2,  # kW
                'variance': 0.8,
                'unit': 'kW'
            },
            'home_gas_001': {
                'type': 'gas_meter',
                'location': 'Natural gas line',
                'baseline': 1.5,  # m³/hour
                'variance': 0.4,
                'unit': 'm3/h'
            },
            
            # Vehicle monitoring
            'vehicle_obd_001': {
                'type': 'obd_scanner',
                'location': 'Vehicle OBD port',
                'baseline': 8.5,  # L/100km
                'variance': 2.0,
                'unit': 'L/100km'
            },
            'vehicle_gps_001': {
                'type': 'gps_tracker',
                'location': 'Vehicle',
                'baseline': 45.0,  # km/h average speed
                'variance': 15.0,
                'unit': 'km/h'
            },
            
            # Air quality monitoring
            'air_quality_001': {
                'type': 'air_quality',
                'location': 'Outdoor ambient',
                'baseline': 65.0,  # AQI
                'variance': 25.0,
                'unit': 'AQI'
            },
            'co2_sensor_001': {
                'type': 'co2_monitor',
                'location': 'Indoor air',
                'baseline': 420.0,  # ppm
                'variance': 80.0,
                'unit': 'ppm'
            },
            
            # Smart home devices
            'thermostat_001': {
                'type': 'smart_thermostat',
                'location': 'Living room',
                'baseline': 22.0,  # °C
                'variance': 3.0,
                'unit': 'celsius'
            },
            'smart_plug_001': {
                'type': 'smart_plug',
                'location': 'Home office',
                'baseline': 150.0,  # watts
                'variance': 50.0,
                'unit': 'watts'
            },
            
            # Waste monitoring
            'waste_scale_001': {
                'type': 'waste_scale',
                'location': 'Kitchen bin',
                'baseline': 2.5,  # kg/day
                'variance': 1.0,
                'unit': 'kg'
            },
            
            # Transportation
            'bike_tracker_001': {
                'type': 'bike_computer',
                'location': 'Bicycle',
                'baseline': 0.0,  # km/day
                'variance': 5.0,
                'unit': 'km'
            }
        }
    
    async def get_real_time_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Get a real-time reading from a specific sensor"""
        
        if sensor_id not in self.sensors:
            return None
        
        sensor = self.sensors[sensor_id]
        
        # Simulate realistic sensor data with patterns
        value = self._generate_realistic_value(sensor)
        quality = self._determine_data_quality()
        battery = random.uniform(0.3, 1.0) if random.random() > 0.3 else None
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor['type'],
            location=sensor['location'],
            value=round(value, 2),
            unit=sensor['unit'],
            timestamp=datetime.now(),
            quality=quality,
            battery_level=battery
        )
        
        self.readings_history.append(reading)
        return reading
    
    async def get_sensor_data_batch(self, sensor_ids: List[str] = None,
                                  duration_minutes: int = 60) -> List[SensorReading]:
        """Get batch readings from multiple sensors over time period"""
        
        if sensor_ids is None:
            sensor_ids = list(self.sensors.keys())
        
        readings = []
        current_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # Generate readings every 5 minutes for the duration
        while current_time <= datetime.now():
            for sensor_id in sensor_ids:
                if sensor_id in self.sensors:
                    sensor = self.sensors[sensor_id]
                    value = self._generate_realistic_value(sensor, current_time)
                    
                    reading = SensorReading(
                        sensor_id=sensor_id,
                        sensor_type=sensor['type'],
                        location=sensor['location'],
                        value=round(value, 2),
                        unit=sensor['unit'],
                        timestamp=current_time,
                        quality=self._determine_data_quality(),
                        battery_level=random.uniform(0.4, 1.0)
                    )
                    readings.append(reading)
            
            current_time += timedelta(minutes=5)
        
        return readings
    
    def _generate_realistic_value(self, sensor: Dict[str, Any], 
                                timestamp: datetime = None) -> float:
        """Generate realistic sensor values with time-based patterns"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        baseline = sensor['baseline']
        variance = sensor['variance']
        sensor_type = sensor['type']
        
        # Add time-based patterns
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base random variation
        value = baseline + random.gauss(0, variance / 3)
        
        # Add realistic patterns based on sensor type
        if sensor_type == 'energy_meter':
            # Higher usage in morning and evening
            if 6 <= hour <= 9 or 17 <= hour <= 22:
                value *= 1.3
            elif 23 <= hour or hour <= 5:
                value *= 0.6
            # Weekend patterns
            if day_of_week >= 5:  # Weekend
                value *= 1.1
                
        elif sensor_type == 'obd_scanner':
            # Higher consumption in traffic hours
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                value *= 1.4
            # Lower on weekends
            if day_of_week >= 5:
                value *= 0.8
                
        elif sensor_type == 'air_quality':
            # Worse air quality during rush hours
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                value *= 1.2
            # Better at night
            if 22 <= hour or hour <= 6:
                value *= 0.85
                
        elif sensor_type == 'smart_thermostat':
            # Temperature adjustments based on time
            if 6 <= hour <= 8:  # Morning warm-up
                value += 2
            elif 22 <= hour:  # Night cool-down
                value -= 2
                
        elif sensor_type == 'waste_scale':
            # More waste in evenings
            if 18 <= hour <= 22:
                value *= 1.5
            elif hour <= 8:
                value *= 0.3
        
        return max(0, value)  # Ensure non-negative values
    
    def _determine_data_quality(self) -> str:
        """Simulate data quality issues"""
        rand = random.random()
        if rand < 0.8:
            return 'high'
        elif rand < 0.95:
            return 'medium'
        else:
            return 'low'
    
    async def verify_carbon_activity(self, activity_type: str,
                                   claimed_value: float,
                                   location: str,
                                   timeframe: datetime) -> Dict[str, Any]:
        """Verify carbon activities using relevant IoT sensors"""
        
        verification_result = {
            'activity_type': activity_type,
            'claimed_value': claimed_value,
            'verification_method': 'iot_sensors',
            'sensor_data': [],
            'verification_confidence': 0.0,
            'verified': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Select relevant sensors based on activity type
        relevant_sensors = self._get_relevant_sensors(activity_type)
        
        if not relevant_sensors:
            verification_result['verification_confidence'] = 0.1
            verification_result['notes'] = 'No relevant sensors available'
            return verification_result
        
        # Get sensor readings around the claimed timeframe
        start_time = timeframe - timedelta(minutes=30)
        end_time = timeframe + timedelta(minutes=30)
        
        for sensor_id in relevant_sensors:
            readings = await self._get_historical_readings(sensor_id, start_time, end_time)
            if readings:
                verification_result['sensor_data'].append({
                    'sensor_id': sensor_id,
                    'sensor_type': self.sensors[sensor_id]['type'],
                    'readings_count': len(readings),
                    'average_value': sum(r.value for r in readings) / len(readings),
                    'data_quality': readings[0].quality if readings else 'unknown'
                })
        
        # Calculate verification confidence
        verification_confidence = self._calculate_verification_confidence(
            activity_type, claimed_value, verification_result['sensor_data']
        )
        
        verification_result['verification_confidence'] = verification_confidence
        verification_result['verified'] = verification_confidence > 0.7
        
        return verification_result
    
    def _get_relevant_sensors(self, activity_type: str) -> List[str]:
        """Get sensors relevant to specific activity types"""
        sensor_mapping = {
            'transport_car': ['vehicle_obd_001', 'vehicle_gps_001'],
            'transport_bike': ['bike_tracker_001'],
            'energy_home': ['home_energy_001', 'home_gas_001', 'thermostat_001'],
            'energy_office': ['smart_plug_001'],
            'waste_disposal': ['waste_scale_001'],
            'air_quality': ['air_quality_001', 'co2_sensor_001']
        }
        
        return sensor_mapping.get(activity_type, [])
    
    async def _get_historical_readings(self, sensor_id: str,
                                     start_time: datetime,
                                     end_time: datetime) -> List[SensorReading]:
        """Get historical readings for a sensor in time range"""
        # Simulate historical data
        readings = []
        current_time = start_time
        
        while current_time <= end_time:
            if sensor_id in self.sensors:
                sensor = self.sensors[sensor_id]
                value = self._generate_realistic_value(sensor, current_time)
                
                reading = SensorReading(
                    sensor_id=sensor_id,
                    sensor_type=sensor['type'],
                    location=sensor['location'],
                    value=round(value, 2),
                    unit=sensor['unit'],
                    timestamp=current_time,
                    quality=self._determine_data_quality()
                )
                readings.append(reading)
            
            current_time += timedelta(minutes=10)
        
        return readings
    
    def _calculate_verification_confidence(self, activity_type: str,
                                         claimed_value: float,
                                         sensor_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for verification"""
        
        if not sensor_data:
            return 0.1
        
        confidence = 0.5  # Base confidence
        
        # Add confidence based on data quality and consistency
        high_quality_sensors = sum(1 for s in sensor_data if s.get('data_quality') == 'high')
        confidence += (high_quality_sensors / len(sensor_data)) * 0.3
        
        # Add confidence based on number of sensors
        if len(sensor_data) >= 2:
            confidence += 0.15
        
        # Activity-specific validation
        if activity_type == 'transport_car':
            # Check if OBD and GPS data are consistent
            obd_data = next((s for s in sensor_data if 'obd' in s['sensor_id']), None)
            gps_data = next((s for s in sensor_data if 'gps' in s['sensor_id']), None)
            
            if obd_data and gps_data:
                # Simplified consistency check
                confidence += 0.2
        
        elif activity_type == 'energy_home':
            # Check if energy readings match claimed usage
            energy_data = next((s for s in sensor_data if 'energy' in s['sensor_id']), None)
            if energy_data:
                reading_avg = energy_data['average_value']
                # Convert claimed kWh to average kW (simplified)
                claimed_kw = claimed_value / 24  # Assume daily kWh
                accuracy = 1 - abs(reading_avg - claimed_kw) / claimed_kw
                confidence += accuracy * 0.25
        
        return min(confidence, 0.95)  # Cap at 95%
    
    async def get_sensor_status(self) -> Dict[str, Any]:
        """Get status of all sensors"""
        status = {
            'total_sensors': len(self.sensors),
            'active_sensors': 0,
            'sensors_by_type': {},
            'overall_health': 'good',
            'last_update': datetime.now().isoformat(),
            'sensor_details': []
        }
        
        for sensor_id, sensor in self.sensors.items():
            # Simulate sensor health
            health = random.choice(['good', 'good', 'good', 'warning', 'error'])
            if health in ['good', 'warning']:
                status['active_sensors'] += 1
            
            sensor_type = sensor['type']
            if sensor_type not in status['sensors_by_type']:
                status['sensors_by_type'][sensor_type] = 0
            status['sensors_by_type'][sensor_type] += 1
            
            status['sensor_details'].append({
                'sensor_id': sensor_id,
                'type': sensor_type,
                'location': sensor['location'],
                'status': health,
                'battery_level': random.uniform(0.3, 1.0),
                'last_reading': datetime.now() - timedelta(minutes=random.randint(1, 30))
            })
        
        # Determine overall health
        error_count = sum(1 for s in status['sensor_details'] if s['status'] == 'error')
        if error_count > len(self.sensors) * 0.2:
            status['overall_health'] = 'degraded'
        elif error_count > 0:
            status['overall_health'] = 'warning'
        
        return status

# Demo usage functions
async def get_demo_iot_data():
    """Generate demo IoT sensor data for showcase"""
    
    simulator = IoTSensorSimulator()
    
    # Get real-time readings from key sensors
    energy_reading = await simulator.get_real_time_reading('home_energy_001')
    vehicle_reading = await simulator.get_real_time_reading('vehicle_obd_001')
    air_quality_reading = await simulator.get_real_time_reading('air_quality_001')
    
    # Get batch data for trend analysis
    batch_data = await simulator.get_sensor_data_batch(
        ['home_energy_001', 'vehicle_obd_001'], 
        duration_minutes=120
    )
    
    # Verify a carbon activity
    verification = await simulator.verify_carbon_activity(
        'transport_car', 8.5, 'commute_route', datetime.now()
    )
    
    # Get sensor status
    status = await simulator.get_sensor_status()
    
    return {
        'real_time_readings': {
            'energy': asdict(energy_reading) if energy_reading else None,
            'vehicle': asdict(vehicle_reading) if vehicle_reading else None,
            'air_quality': asdict(air_quality_reading) if air_quality_reading else None
        },
        'batch_data_sample': len(batch_data),
        'activity_verification': verification,
        'sensor_network_status': status,
        'demo_timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run demo IoT simulation
    demo_results = asyncio.run(get_demo_iot_data())
    print(json.dumps(demo_results, indent=2, default=str))