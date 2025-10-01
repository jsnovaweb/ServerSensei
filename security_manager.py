import psutil
import platform
import subprocess
import hashlib
import os
from datetime import datetime
from collections import defaultdict

class SecurityManager:
    """
    Comprehensive security monitoring and management.
    Includes port scanning, intrusion detection, and security auditing.
    Cross-platform compatible for Windows, macOS, and Linux.
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.failed_login_attempts = defaultdict(int)
        self.suspicious_processes = []
        self.security_log = []
        self.known_malicious_ports = [
            1337, 31337, 12345, 54321, 6666, 6667,
            6668, 6669, 1243, 1999, 2000, 6711, 6712, 6713
        ]
    
    def run_security_scan(self):
        """Run comprehensive security scan"""
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'open_ports': self.scan_open_ports(),
            'suspicious_processes': self.detect_suspicious_processes(),
            'firewall_status': self.check_firewall_status(),
            'security_score': 0,
            'warnings': [],
            'recommendations': []
        }
        
        results['security_score'] = self._calculate_security_score(results)
        results['warnings'] = self._generate_warnings(results)
        results['recommendations'] = self._generate_recommendations(results)
        
        self._log_security_event('security_scan', results)
        
        return results
    
    def scan_open_ports(self):
        """Scan for open network ports"""
        open_ports = []
        suspicious_ports = []
        
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    if hasattr(conn.laddr, 'port'):
                        port = conn.laddr.port
                        address = conn.laddr.ip
                    else:
                        port = conn.laddr[1] if len(conn.laddr) > 1 else 0
                        address = conn.laddr[0] if len(conn.laddr) > 0 else '0.0.0.0'
                    
                    port_info = {
                        'port': port,
                        'address': address,
                        'pid': conn.pid,
                        'process': self._get_process_name(conn.pid),
                        'suspicious': port in self.known_malicious_ports
                    }
                    
                    open_ports.append(port_info)
                    
                    if port_info['suspicious']:
                        suspicious_ports.append(port_info)
        
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        
        return {
            'total': len(open_ports),
            'ports': open_ports,
            'suspicious': suspicious_ports
        }
    
    def _get_process_name(self, pid):
        """Get process name from PID"""
        if pid is None:
            return 'System'
        
        try:
            proc = psutil.Process(pid)
            return proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 'Unknown'
    
    def detect_suspicious_processes(self):
        """Detect potentially suspicious processes"""
        suspicious = []
        
        suspicious_names = [
            'nc', 'netcat', 'ncat', 'cryptominer', 'miner',
            'xmrig', 'ccminer', 'backdoor', 'rootkit'
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    
                    if any(sus_name in pinfo['name'].lower() for sus_name in suspicious_names):
                        suspicious.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'user': pinfo['username'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo['memory_percent'],
                            'reason': 'Suspicious process name'
                        })
                    
                    elif pinfo['cpu_percent'] > 90 and pinfo['memory_percent'] > 50:
                        suspicious.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'user': pinfo['username'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo['memory_percent'],
                            'reason': 'High resource usage'
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception:
            pass
        
        return suspicious
    
    def check_firewall_status(self):
        """Check firewall status"""
        firewall_info = {
            'enabled': False,
            'status': 'Unknown',
            'details': ''
        }
        
        try:
            if self.os_type == "Linux":
                firewall_info = self._check_linux_firewall()
            elif self.os_type == "Darwin":
                firewall_info = self._check_macos_firewall()
            elif self.os_type == "Windows":
                firewall_info = self._check_windows_firewall()
        
        except Exception as e:
            firewall_info['details'] = f'Error checking firewall: {str(e)}'
        
        return firewall_info
    
    def _check_linux_firewall(self):
        """Check Linux firewall (ufw, iptables)"""
        firewall_info = {'enabled': False, 'status': 'Unknown', 'details': ''}
        
        try:
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout.lower()
                firewall_info['enabled'] = 'active' in output
                firewall_info['status'] = 'Active' if firewall_info['enabled'] else 'Inactive'
                firewall_info['details'] = 'UFW (Uncomplicated Firewall)'
                return firewall_info
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            result = subprocess.run(['iptables', '-L'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                firewall_info['enabled'] = len(result.stdout.strip()) > 100
                firewall_info['status'] = 'Active' if firewall_info['enabled'] else 'Inactive'
                firewall_info['details'] = 'iptables'
                return firewall_info
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            pass
        
        firewall_info['status'] = 'Not detected'
        return firewall_info
    
    def _check_macos_firewall(self):
        """Check macOS firewall"""
        firewall_info = {'enabled': False, 'status': 'Unknown', 'details': ''}
        
        try:
            result = subprocess.run(
                ['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                firewall_info['enabled'] = 'enabled' in output
                firewall_info['status'] = 'Enabled' if firewall_info['enabled'] else 'Disabled'
                firewall_info['details'] = 'macOS Application Firewall'
        
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            firewall_info['status'] = 'Unable to check (requires admin)'
        
        return firewall_info
    
    def _check_windows_firewall(self):
        """Check Windows firewall"""
        firewall_info = {'enabled': False, 'status': 'Unknown', 'details': ''}
        
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                firewall_info['enabled'] = 'on' in output
                firewall_info['status'] = 'ON' if firewall_info['enabled'] else 'OFF'
                firewall_info['details'] = 'Windows Defender Firewall'
        
        except (FileNotFoundError, subprocess.TimeoutExpired):
            firewall_info['status'] = 'Unable to check'
        
        return firewall_info
    
    def check_ssh_security(self, ssh_config_path='/etc/ssh/sshd_config'):
        """Check SSH configuration security"""
        security_issues = []
        
        if not os.path.exists(ssh_config_path):
            return {'checked': False, 'issues': ['SSH config file not found']}
        
        try:
            with open(ssh_config_path, 'r') as f:
                config = f.read()
            
            if 'PermitRootLogin yes' in config:
                security_issues.append('Root login is permitted (security risk)')
            
            if 'PasswordAuthentication yes' in config:
                security_issues.append('Password authentication enabled (consider key-only)')
            
            if 'PermitEmptyPasswords yes' in config:
                security_issues.append('Empty passwords are permitted (critical risk)')
            
            if 'X11Forwarding yes' in config:
                security_issues.append('X11 forwarding enabled (potential risk)')
        
        except (PermissionError, IOError):
            return {'checked': False, 'issues': ['Unable to read SSH config (permission denied)']}
        
        return {
            'checked': True,
            'issues': security_issues if security_issues else ['No major security issues detected']
        }
    
    def get_active_connections(self):
        """Get all active network connections"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.laddr:
                    if hasattr(conn.laddr, 'port'):
                        local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                    else:
                        local_addr = f"{conn.laddr[0]}:{conn.laddr[1]}" if len(conn.laddr) > 1 else 'N/A'
                    
                    if conn.raddr:
                        if hasattr(conn.raddr, 'port'):
                            remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
                        else:
                            remote_addr = f"{conn.raddr[0]}:{conn.raddr[1]}" if len(conn.raddr) > 1 else 'N/A'
                    else:
                        remote_addr = 'N/A'
                    
                    connections.append({
                        'local_address': local_addr,
                        'remote_address': remote_addr,
                        'status': conn.status,
                        'pid': conn.pid,
                        'process': self._get_process_name(conn.pid)
                    })
        
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        
        return connections
    
    def verify_file_integrity(self, file_path):
        """Calculate file hash for integrity verification"""
        if not os.path.exists(file_path):
            return {'exists': False, 'hash': None}
        
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return {
                'exists': True,
                'hash': sha256_hash.hexdigest(),
                'algorithm': 'SHA-256'
            }
        
        except (PermissionError, IOError) as e:
            return {'exists': True, 'hash': None, 'error': str(e)}
    
    def _calculate_security_score(self, results):
        """Calculate overall security score (0-100)"""
        score = 100
        
        if not results['firewall_status']['enabled']:
            score -= 30
        
        if results['open_ports']['suspicious']:
            score -= 20 * len(results['open_ports']['suspicious'])
        
        if results['suspicious_processes']:
            score -= 15 * len(results['suspicious_processes'])
        
        if results['open_ports']['total'] > 10:
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_warnings(self, results):
        """Generate security warnings"""
        warnings = []
        
        if not results['firewall_status']['enabled']:
            warnings.append('⚠️ Firewall is not enabled or not detected')
        
        if results['open_ports']['suspicious']:
            for port in results['open_ports']['suspicious']:
                warnings.append(f'⚠️ Suspicious port {port["port"]} is open ({port["process"]})')
        
        if results['suspicious_processes']:
            for proc in results['suspicious_processes']:
                warnings.append(f'⚠️ Suspicious process: {proc["name"]} - {proc["reason"]}')
        
        if results['open_ports']['total'] > 15:
            warnings.append(f'⚠️ High number of open ports detected ({results["open_ports"]["total"]})')
        
        return warnings
    
    def _generate_recommendations(self, results):
        """Generate security recommendations"""
        recommendations = []
        
        if not results['firewall_status']['enabled']:
            recommendations.append('🔒 Enable firewall protection')
        
        if results['open_ports']['suspicious']:
            recommendations.append('🔒 Close suspicious ports and investigate associated processes')
        
        if results['suspicious_processes']:
            recommendations.append('🔒 Review and terminate suspicious processes')
        
        if results['security_score'] < 70:
            recommendations.append('🔒 Perform a comprehensive security audit')
            recommendations.append('🔒 Update system and software to latest versions')
            recommendations.append('🔒 Enable SSH key-only authentication')
        
        if not recommendations:
            recommendations.append('✅ System security appears to be in good condition')
        
        return recommendations
    
    def _log_security_event(self, event_type, data):
        """Log security events"""
        self.security_log.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'data': data
        })
        
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
    
    def get_security_log(self, limit=100):
        """Get recent security log entries"""
        return self.security_log[-limit:]
    
    def encrypt_data(self, data, key=None):
        """Simple data encryption for sensitive information"""
        if key is None:
            key = hashlib.sha256(os.urandom(32)).digest()
        
        encrypted = hashlib.pbkdf2_hmac('sha256', data.encode(), key, 100000)
        
        return {
            'encrypted': encrypted.hex(),
            'algorithm': 'PBKDF2-HMAC-SHA256'
        }
    
    def check_system_updates(self):
        """Check if system updates are available"""
        updates_info = {
            'checked': False,
            'updates_available': False,
            'count': 0,
            'details': ''
        }
        
        try:
            if self.os_type == "Linux":
                result = subprocess.run(['apt', 'list', '--upgradable'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    updates_count = len([l for l in lines if '/' in l]) - 1
                    updates_info['checked'] = True
                    updates_info['updates_available'] = updates_count > 0
                    updates_info['count'] = max(0, updates_count)
                    updates_info['details'] = f'{updates_count} updates available'
            
            elif self.os_type == "Darwin":
                result = subprocess.run(['softwareupdate', '-l'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    updates_info['checked'] = True
                    updates_info['updates_available'] = 'No new software available' not in result.stdout
                    updates_info['details'] = 'Check App Store for updates'
            
            elif self.os_type == "Windows":
                updates_info['checked'] = True
                updates_info['details'] = 'Check Windows Update manually'
        
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            updates_info['details'] = 'Unable to check for updates'
        
        return updates_info
