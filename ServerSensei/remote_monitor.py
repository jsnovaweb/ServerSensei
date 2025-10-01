import json
from datetime import datetime

class RemoteSystemMonitor:
    """
    Remote system monitoring using SSH to execute commands on remote servers.
    Supports Linux, macOS, and Windows (via PowerShell over SSH).
    """
    
    def __init__(self, ssh_manager):
        self.ssh = ssh_manager
        self.net_io_start = None
        self.last_check_time = None
    
    def get_cpu_usage(self):
        """Get CPU usage from remote server"""
        if not self.ssh.is_remote():
            return 0
        
        output, error = self.ssh.execute_command(
            "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}' || "
            "sar 1 1 | awk 'NR==4 {print 100-$NF}' || "
            "powershell -Command \"(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples[0].CookedValue\""
        )
        
        if output:
            try:
                return float(output)
            except:
                return 0
        return 0
    
    def get_memory_info(self):
        """Get memory information from remote server"""
        if not self.ssh.is_remote():
            return {}
        
        output, error = self.ssh.execute_command(
            "free -b | grep Mem | awk '{print $2,$3,$4,$7}' || "
            "vm_stat | awk '/Pages free/ {free=$3} /Pages active/ {active=$3} /Pages inactive/ {inactive=$3} /Pages wired/ {wired=$3} END {print (free+active+inactive+wired)*4096, (active+wired)*4096, free*4096, free*4096}' || "
            "powershell -Command \"$mem = Get-WmiObject Win32_OperatingSystem; Write-Host $mem.TotalVisibleMemorySize*1024 $mem.FreePhysicalMemory*1024\""
        )
        
        if output:
            try:
                parts = output.split()
                total = int(parts[0])
                used = int(parts[1]) if len(parts) > 1 else 0
                available = int(parts[2]) if len(parts) > 2 else total - used
                
                percent = (used / total * 100) if total > 0 else 0
                
                return {
                    'total': total,
                    'available': available,
                    'used': used,
                    'percent': percent,
                    'total_gb': total / (1024**3),
                    'used_gb': used / (1024**3),
                    'available_gb': available / (1024**3)
                }
            except:
                return {}
        return {}
    
    def get_disk_usage(self):
        """Get disk usage from remote server"""
        if not self.ssh.is_remote():
            return []
        
        output, error = self.ssh.execute_command(
            "df -B1 | awk 'NR>1 {print $1,$6,$2,$3,$4,$5}' || "
            "df -b | awk 'NR>1 {print $1,$9,$2,$3,$4,$5}' || "
            "powershell -Command \"Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -ne $null} | ForEach-Object {Write-Host $_.Name $_.Root ($_.Used+$_.Free) $_.Used $_.Free ([math]::Round($_.Used/($_.Used+$_.Free)*100,1))}\""
        )
        
        if output:
            disk_info = []
            for line in output.strip().split('\n'):
                try:
                    parts = line.split()
                    if len(parts) >= 6:
                        device = parts[0]
                        mountpoint = parts[1]
                        total = int(parts[2])
                        used = int(parts[3])
                        free = int(parts[4])
                        percent = float(parts[5].rstrip('%'))
                        
                        disk_info.append({
                            'device': device,
                            'mountpoint': mountpoint,
                            'fstype': 'unknown',
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': percent,
                            'total_gb': total / (1024**3),
                            'used_gb': used / (1024**3),
                            'free_gb': free / (1024**3)
                        })
                except:
                    continue
            return disk_info
        return []
    
    def get_network_activity(self):
        """Get network activity from remote server"""
        if not self.ssh.is_remote():
            return {}
        
        output, error = self.ssh.execute_command(
            "cat /proc/net/dev | awk 'NR>2 {recv+=$2; sent+=$10} END {print recv, sent}' || "
            "netstat -ib | awk 'NR>1 {recv+=$7; sent+=$10} END {print recv, sent}' || "
            "powershell -Command \"$net = Get-NetAdapterStatistics; $recv = ($net | Measure-Object -Property ReceivedBytes -Sum).Sum; $sent = ($net | Measure-Object -Property SentBytes -Sum).Sum; Write-Host $recv $sent\""
        )
        
        if output:
            try:
                parts = output.split()
                current_recv = int(parts[0])
                current_sent = int(parts[1])
                
                current_time = datetime.now()
                
                if self.net_io_start and self.last_check_time:
                    time_diff = (current_time - self.last_check_time).total_seconds()
                    if time_diff > 0:
                        upload_speed = (current_sent - self.net_io_start[1]) / time_diff
                        download_speed = (current_recv - self.net_io_start[0]) / time_diff
                    else:
                        upload_speed = 0
                        download_speed = 0
                else:
                    upload_speed = 0
                    download_speed = 0
                
                self.net_io_start = (current_recv, current_sent)
                self.last_check_time = current_time
                
                return {
                    'upload_speed': upload_speed,
                    'download_speed': download_speed,
                    'upload_speed_mb': upload_speed / (1024**2),
                    'download_speed_mb': download_speed / (1024**2),
                    'bytes_sent': current_sent,
                    'bytes_recv': current_recv
                }
            except:
                return {}
        return {}
    
    def get_processes(self):
        """Get list of running processes from remote server"""
        if not self.ssh.is_remote():
            return []
        
        output, error = self.ssh.execute_command(
            "ps aux | awk 'NR>1 {print $2,$11,$3,$4,$8}' | head -100 || "
            "ps aux | awk 'NR>1 {print $2,$10,$3,$4,$8}' | head -100 || "
            "powershell -Command \"Get-Process | Select-Object -First 100 | ForEach-Object {Write-Host $_.Id $_.ProcessName $_.CPU $_.WorkingSet64 'running'}\""
        )
        
        if output:
            processes = []
            for line in output.strip().split('\n'):
                try:
                    parts = line.split()
                    if len(parts) >= 4:
                        pid = int(parts[0])
                        name = parts[1]
                        cpu_percent = float(parts[2]) if parts[2].replace('.', '').isdigit() else 0
                        mem_percent = float(parts[3]) if parts[3].replace('.', '').isdigit() else 0
                        status = parts[4] if len(parts) > 4 else 'unknown'
                        
                        processes.append({
                            'pid': pid,
                            'name': name,
                            'cpu_percent': cpu_percent,
                            'memory_percent': mem_percent,
                            'status': status
                        })
                except:
                    continue
            return processes
        return []
    
    def get_system_info(self):
        """Get system information from remote server"""
        if not self.ssh.is_remote():
            return {}
        
        os_info, _ = self.ssh.execute_command("uname -s || powershell -Command \"(Get-WmiObject Win32_OperatingSystem).Caption\"")
        version_info, _ = self.ssh.execute_command("uname -r || powershell -Command \"(Get-WmiObject Win32_OperatingSystem).Version\"")
        arch_info, _ = self.ssh.execute_command("uname -m || powershell -Command \"(Get-WmiObject Win32_Processor).Architecture\"")
        hostname_info, _ = self.ssh.execute_command("hostname")
        uptime_info, _ = self.ssh.execute_command(
            "uptime -s 2>/dev/null || who -b | awk '{print $3,$4}' || powershell -Command \"(Get-CimInstance Win32_OperatingSystem).LastBootUpTime\""
        )
        cpu_count, _ = self.ssh.execute_command("nproc || sysctl -n hw.ncpu || powershell -Command \"(Get-WmiObject Win32_Processor).NumberOfCores\"")
        
        return {
            'os': os_info.strip() if os_info else 'Unknown',
            'os_version': version_info.strip() if version_info else 'Unknown',
            'os_release': version_info.strip() if version_info else 'Unknown',
            'architecture': arch_info.strip() if arch_info else 'Unknown',
            'processor': 'Remote CPU',
            'hostname': hostname_info.strip() if hostname_info else 'Unknown',
            'boot_time': uptime_info.strip() if uptime_info else 'Unknown',
            'uptime': 'N/A (remote)',
            'cpu_count': int(cpu_count.strip()) if cpu_count and cpu_count.strip().isdigit() else 0,
            'cpu_count_logical': int(cpu_count.strip()) if cpu_count and cpu_count.strip().isdigit() else 0
        }
    
    def kill_process(self, pid):
        """Kill a process on remote server"""
        if not self.ssh.is_remote():
            return False, "Not connected to remote server"
        
        output, error = self.ssh.execute_command(f"kill {pid} || taskkill /PID {pid} /F")
        
        if error:
            return False, f"Failed to kill process {pid}: {error}"
        return True, f"Process {pid} terminated successfully"
