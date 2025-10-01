import os
import platform
import shutil
import psutil
import gc

class SystemOptimizer:
    """
    System optimization tools for clearing cache, freeing memory,
    and performing cleanup tasks across Windows, macOS, and Linux.
    """
    
    def __init__(self):
        self.os_type = platform.system()
    
    def get_temp_directories(self):
        """Get temporary directories based on OS"""
        temp_dirs = []
        
        if self.os_type == "Windows":
            temp_dirs.append(os.environ.get('TEMP', ''))
            temp_dirs.append(os.environ.get('TMP', ''))
            temp_dirs.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'))
        elif self.os_type == "Darwin":
            temp_dirs.append('/private/tmp')
            temp_dirs.append(os.path.expanduser('~/Library/Caches'))
        elif self.os_type == "Linux":
            temp_dirs.append('/tmp')
            temp_dirs.append(os.path.expanduser('~/.cache'))
        
        return [d for d in temp_dirs if d and os.path.exists(d)]
    
    def clear_temp_files(self):
        """Clear temporary files from system temp directories"""
        results = []
        temp_dirs = self.get_temp_directories()
        
        for temp_dir in temp_dirs:
            try:
                deleted_count = 0
                freed_space = 0
                
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            os.remove(item_path)
                            deleted_count += 1
                            freed_space += size
                        elif os.path.isdir(item_path):
                            size = self._get_dir_size(item_path)
                            shutil.rmtree(item_path)
                            deleted_count += 1
                            freed_space += size
                    except (PermissionError, OSError):
                        continue
                
                results.append({
                    'directory': temp_dir,
                    'files_deleted': deleted_count,
                    'space_freed_mb': freed_space / (1024**2)
                })
            except Exception as e:
                results.append({
                    'directory': temp_dir,
                    'error': str(e)
                })
        
        return results
    
    def _get_dir_size(self, path):
        """Get total size of directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (PermissionError, OSError):
            pass
        return total_size
    
    def free_memory(self):
        """
        Attempt to free unused memory.
        Note: This is limited in effectiveness as the OS manages memory.
        """
        gc.collect()
        
        mem_before = psutil.virtual_memory()
        
        if self.os_type == "Linux":
            try:
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3\n')
            except (PermissionError, OSError):
                pass
        
        mem_after = psutil.virtual_memory()
        
        return {
            'before_available_mb': mem_before.available / (1024**2),
            'after_available_mb': mem_after.available / (1024**2),
            'freed_mb': (mem_after.available - mem_before.available) / (1024**2)
        }
    
    def kill_unresponsive_processes(self):
        """Find and kill unresponsive processes"""
        killed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                if proc.info['status'] in ['zombie', 'stopped']:
                    proc.terminate()
                    killed_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return killed_processes
    
    def quick_optimize(self):
        """Run all safe optimization tasks"""
        results = {
            'temp_files': self.clear_temp_files(),
            'memory': self.free_memory(),
            'unresponsive_processes': self.kill_unresponsive_processes()
        }
        return results
    
    def get_optimization_summary(self, results):
        """Generate a summary of optimization results"""
        summary = []
        
        if 'temp_files' in results:
            total_files = sum(r.get('files_deleted', 0) for r in results['temp_files'])
            total_space = sum(r.get('space_freed_mb', 0) for r in results['temp_files'])
            summary.append(f"Deleted {total_files} temporary files")
            summary.append(f"Freed {total_space:.2f} MB of disk space")
        
        if 'memory' in results:
            freed_mem = results['memory'].get('freed_mb', 0)
            summary.append(f"Freed {freed_mem:.2f} MB of RAM")
        
        if 'unresponsive_processes' in results:
            killed_count = len(results['unresponsive_processes'])
            summary.append(f"Terminated {killed_count} unresponsive processes")
        
        return summary
