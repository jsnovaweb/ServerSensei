import os
import platform
import psutil
import subprocess

class DeviceManager:
    """
    Device detection and management for USB drives, external storage,
    and other connected devices. Cross-platform support.
    """
    
    def __init__(self):
        self.os_type = platform.system()
    
    def get_connected_devices(self):
        """Get list of connected storage devices"""
        devices = []
        
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                is_removable = self._is_removable(partition)
                
                device_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'total_gb': usage.total / (1024**3),
                    'used_gb': usage.used / (1024**3),
                    'free_gb': usage.free / (1024**3),
                    'percent': usage.percent,
                    'removable': is_removable
                }
                devices.append(device_info)
            except (PermissionError, OSError):
                continue
        
        return devices
    
    def _is_removable(self, partition):
        """Check if a partition is removable (USB, external drive)"""
        if self.os_type == "Windows":
            try:
                import ctypes
                drive_root = partition.mountpoint
                if not drive_root.endswith('\\'):
                    drive_root += '\\'
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_root)  # type: ignore
                DRIVE_REMOVABLE = 2
                return drive_type == DRIVE_REMOVABLE
            except:
                return False
        
        elif self.os_type == "Linux":
            device_name = partition.device.replace('/dev/', '')
            try:
                removable_path = f'/sys/block/{device_name}/removable'
                if 'sd' in device_name or 'mmc' in device_name:
                    base_device = device_name.rstrip('0123456789')
                    removable_path = f'/sys/block/{base_device}/removable'
                
                if os.path.exists(removable_path):
                    with open(removable_path, 'r') as f:
                        return f.read().strip() == '1'
            except:
                pass
            
            if '/media/' in partition.mountpoint or '/mnt/' in partition.mountpoint:
                return True
            return False
        
        elif self.os_type == "Darwin":
            if '/Volumes/' in partition.mountpoint and partition.mountpoint != '/':
                return True
            return False
        
        return False
    
    def eject_device(self, mountpoint):
        """
        Safely eject/unmount a device.
        Works on Linux and macOS. Windows requires different approach.
        """
        try:
            if self.os_type == "Linux":
                subprocess.run(['umount', mountpoint], check=True)
                return True, f"Device {mountpoint} unmounted successfully"
            
            elif self.os_type == "Darwin":
                subprocess.run(['diskutil', 'eject', mountpoint], check=True)
                return True, f"Device {mountpoint} ejected successfully"
            
            elif self.os_type == "Windows":
                return False, "Automatic eject not supported on Windows. Please use 'Safely Remove Hardware'."
            
            return False, "Unsupported operating system"
        
        except subprocess.CalledProcessError as e:
            return False, f"Failed to eject device: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_usb_devices_info(self):
        """Get detailed USB device information (Linux-specific)"""
        usb_devices = []
        
        if self.os_type == "Linux":
            try:
                result = subprocess.run(['lsusb'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        usb_devices.append(line)
            except FileNotFoundError:
                pass
        
        return usb_devices
