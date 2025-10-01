import psutil
import platform
from datetime import datetime, timedelta

class SystemMonitor:
    """
    System monitoring class using psutil to gather system information.
    Cross-platform compatible for Windows, macOS, and Linux.
    """
    
    def __init__(self):
        self.net_io_start = psutil.net_io_counters()
        self.last_check_time = datetime.now()
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_cpu_per_core(self):
        """Get CPU usage per core"""
        return psutil.cpu_percent(interval=0.1, percpu=True)
    
    def get_memory_info(self):
        """Get RAM usage information"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'total_gb': mem.total / (1024**3),
            'used_gb': mem.used / (1024**3),
            'available_gb': mem.available / (1024**3)
        }
    
    def get_disk_usage(self):
        """Get disk usage for all partitions"""
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'total_gb': usage.total / (1024**3),
                    'used_gb': usage.used / (1024**3),
                    'free_gb': usage.free / (1024**3)
                })
            except PermissionError:
                continue
        return disk_info
    
    def get_network_activity(self):
        """Get network upload/download speeds"""
        current_net_io = psutil.net_io_counters()
        current_time = datetime.now()
        
        time_diff = (current_time - self.last_check_time).total_seconds()
        
        if time_diff > 0:
            upload_speed = (current_net_io.bytes_sent - self.net_io_start.bytes_sent) / time_diff
            download_speed = (current_net_io.bytes_recv - self.net_io_start.bytes_recv) / time_diff
        else:
            upload_speed = 0
            download_speed = 0
        
        self.net_io_start = current_net_io
        self.last_check_time = current_time
        
        return {
            'upload_speed': upload_speed,
            'download_speed': download_speed,
            'upload_speed_mb': upload_speed / (1024**2),
            'download_speed_mb': download_speed / (1024**2),
            'bytes_sent': current_net_io.bytes_sent,
            'bytes_recv': current_net_io.bytes_recv
        }
    
    def get_processes(self):
        """Get list of running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def kill_process(self, pid):
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True, f"Process {pid} terminated successfully"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except psutil.AccessDenied:
            return False, f"Access denied to terminate process {pid}"
        except Exception as e:
            return False, f"Error terminating process {pid}: {str(e)}"
    
    def get_system_info(self):
        """Get system information"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': str(uptime).split('.')[0],
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True)
        }
    
    def get_disk_io(self):
        """Get disk I/O statistics"""
        disk_io = psutil.disk_io_counters()
        if disk_io:
            return {
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_mb': disk_io.read_bytes / (1024**2),
                'write_mb': disk_io.write_bytes / (1024**2)
            }
        return None
    
    def get_cpu_frequency(self):
        """Get CPU frequency information"""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return {
                    'current': freq.current,
                    'min': freq.min,
                    'max': freq.max
                }
        except AttributeError:
            pass
        return {'current': 0, 'min': 0, 'max': 0}
    
    def get_temperatures(self):
        """Get temperature sensors information"""
        temps = []
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temp_dict = psutil.sensors_temperatures()
                if temp_dict:
                    for name, entries in temp_dict.items():
                        for entry in entries:
                            temps.append({
                                'sensor': name,
                                'label': entry.label or 'Unknown',
                                'current': entry.current,
                                'high': entry.high if entry.high else 0,
                                'critical': entry.critical if entry.critical else 0
                            })
        except AttributeError:
            pass
        
        if not temps:
            temps = [{
                'sensor': 'N/A',
                'label': 'No sensors detected',
                'current': 0,
                'high': 0,
                'critical': 0
            }]
        
        return temps
