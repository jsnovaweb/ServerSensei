import platform
import subprocess
import psutil
from datetime import datetime

class ResourceMonitor:
    """
    Advanced resource monitoring for GPU, battery, and temperature sensors.
    Cross-platform compatible for Windows, macOS, and Linux.
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.gpu_available = self._check_gpu_support()
    
    def _check_gpu_support(self):
        """Check if GPU monitoring is available"""
        try:
            import GPUtil
            return True
        except ImportError:
            return False
    
    def get_gpu_info(self):
        """Get GPU load, memory usage, and temperature"""
        gpu_info = []
        
        if not self.gpu_available:
            try:
                import GPUtil
                self.gpu_available = True
            except ImportError:
                return [{
                    'id': 0,
                    'name': 'No GPU detected',
                    'load': 0,
                    'memory_used': 0,
                    'memory_total': 0,
                    'memory_percent': 0,
                    'temperature': 0
                }]
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_percent': gpu.memoryUtil * 100,
                    'temperature': gpu.temperature
                })
        except Exception as e:
            if self.os_type == "Linux":
                gpu_info = self._get_linux_gpu_info()
            elif self.os_type == "Darwin":
                gpu_info = self._get_macos_gpu_info()
            elif self.os_type == "Windows":
                gpu_info = self._get_windows_gpu_info()
        
        if not gpu_info:
            gpu_info = [{
                'id': 0,
                'name': 'GPU unavailable',
                'load': 0,
                'memory_used': 0,
                'memory_total': 0,
                'memory_percent': 0,
                'temperature': 0
            }]
        
        return gpu_info
    
    def _get_linux_gpu_info(self):
        """Get GPU info on Linux using nvidia-smi"""
        gpu_info = []
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 6:
                        gpu_info.append({
                            'id': int(parts[0]),
                            'name': parts[1],
                            'load': float(parts[2]),
                            'memory_used': float(parts[3]),
                            'memory_total': float(parts[4]),
                            'memory_percent': (float(parts[3]) / float(parts[4]) * 100) if float(parts[4]) > 0 else 0,
                            'temperature': float(parts[5])
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
        
        return gpu_info
    
    def _get_macos_gpu_info(self):
        """Get GPU info on macOS"""
        gpu_info = []
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_info.append({
                    'id': 0,
                    'name': 'Apple GPU',
                    'load': 0,
                    'memory_used': 0,
                    'memory_total': 0,
                    'memory_percent': 0,
                    'temperature': 0
                })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return gpu_info
    
    def _get_windows_gpu_info(self):
        """Get GPU info on Windows using WMI"""
        gpu_info = []
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                for idx, line in enumerate(lines):
                    name = line.strip()
                    if name:
                        gpu_info.append({
                            'id': idx,
                            'name': name,
                            'load': 0,
                            'memory_used': 0,
                            'memory_total': 0,
                            'memory_percent': 0,
                            'temperature': 0
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return gpu_info
    
    def get_battery_info(self):
        """Get battery health and status"""
        battery_info = {
            'present': False,
            'percent': 0,
            'power_plugged': False,
            'time_left': 'N/A',
            'health': 'Unknown'
        }
        
        try:
            battery = psutil.sensors_battery()
            
            if battery:
                battery_info['present'] = True
                battery_info['percent'] = battery.percent
                battery_info['power_plugged'] = battery.power_plugged
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    battery_info['time_left'] = f"{hours}h {minutes}m"
                elif battery.power_plugged:
                    battery_info['time_left'] = 'Charging'
                else:
                    battery_info['time_left'] = 'Calculating...'
                
                if battery.percent >= 80:
                    battery_info['health'] = 'Excellent'
                elif battery.percent >= 50:
                    battery_info['health'] = 'Good'
                elif battery.percent >= 20:
                    battery_info['health'] = 'Fair'
                else:
                    battery_info['health'] = 'Poor'
        except AttributeError:
            pass
        except Exception as e:
            battery_info['health'] = f'Error: {str(e)}'
        
        return battery_info
    
    def get_temperature_sensors(self):
        """Get temperature from all available sensors"""
        temp_info = []
        
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            temp_info.append({
                                'sensor': name,
                                'label': entry.label or 'Unknown',
                                'current': entry.current,
                                'high': entry.high if entry.high else 0,
                                'critical': entry.critical if entry.critical else 0
                            })
        except AttributeError:
            pass
        except Exception as e:
            temp_info.append({
                'sensor': 'Error',
                'label': str(e),
                'current': 0,
                'high': 0,
                'critical': 0
            })
        
        if not temp_info:
            if self.os_type == "Linux":
                temp_info = self._get_linux_temperatures()
            elif self.os_type == "Darwin":
                temp_info = self._get_macos_temperatures()
            elif self.os_type == "Windows":
                temp_info = self._get_windows_temperatures()
        
        if not temp_info:
            temp_info = [{
                'sensor': 'N/A',
                'label': 'No temperature sensors detected',
                'current': 0,
                'high': 0,
                'critical': 0
            }]
        
        return temp_info
    
    def _get_linux_temperatures(self):
        """Get temperatures on Linux from /sys/class/thermal"""
        temp_info = []
        
        try:
            import os
            thermal_dir = '/sys/class/thermal'
            
            if os.path.exists(thermal_dir):
                for zone in os.listdir(thermal_dir):
                    if zone.startswith('thermal_zone'):
                        temp_file = os.path.join(thermal_dir, zone, 'temp')
                        type_file = os.path.join(thermal_dir, zone, 'type')
                        
                        if os.path.exists(temp_file):
                            with open(temp_file, 'r') as f:
                                temp = float(f.read().strip()) / 1000.0
                            
                            sensor_type = 'Unknown'
                            if os.path.exists(type_file):
                                with open(type_file, 'r') as f:
                                    sensor_type = f.read().strip()
                            
                            temp_info.append({
                                'sensor': zone,
                                'label': sensor_type,
                                'current': temp,
                                'high': 85.0,
                                'critical': 100.0
                            })
        except Exception:
            pass
        
        return temp_info
    
    def _get_macos_temperatures(self):
        """Get temperatures on macOS"""
        temp_info = []
        
        try:
            result = subprocess.run(['sudo', 'powermetrics', '-n', '1', '-i', '1000'], 
                                   capture_output=True, text=True, timeout=3)
            
            if 'CPU die temperature' in result.stdout:
                temp_info.append({
                    'sensor': 'CPU',
                    'label': 'CPU Die',
                    'current': 0,
                    'high': 85.0,
                    'critical': 100.0
                })
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            pass
        
        return temp_info
    
    def _get_windows_temperatures(self):
        """Get temperatures on Windows"""
        temp_info = []
        
        try:
            result = subprocess.run(
                ['wmic', '/namespace:\\\\root\\wmi', 'PATH', 'MSAcpi_ThermalZoneTemperature', 'get', 'CurrentTemperature'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                for idx, line in enumerate(lines):
                    try:
                        temp_kelvin = float(line.strip())
                        temp_celsius = (temp_kelvin / 10.0) - 273.15
                        
                        temp_info.append({
                            'sensor': f'Zone{idx}',
                            'label': f'Thermal Zone {idx}',
                            'current': temp_celsius,
                            'high': 85.0,
                            'critical': 100.0
                        })
                    except ValueError:
                        continue
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return temp_info
    
    def get_cpu_temperature(self):
        """Get CPU temperature specifically"""
        temps = self.get_temperature_sensors()
        
        for temp in temps:
            if 'cpu' in temp['sensor'].lower() or 'cpu' in temp['label'].lower() or 'core' in temp['label'].lower():
                return temp['current']
        
        if temps and temps[0]['current'] > 0:
            return temps[0]['current']
        
        return 0
