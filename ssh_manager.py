import paramiko
import os
import hashlib
from io import StringIO

class SSHConnectionManager:
    """
    Manages SSH connections to remote servers for monitoring.
    Supports password and SSH key authentication with secure credential handling.
    Enhanced security with host key verification and connection logging.
    """
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.host = None
        self.username = None
        self.connection_type = 'local'
        self.host_keys = {}
        self.connection_log = []
    
    def connect_with_password(self, host, port, username, password):
        """Connect to remote server using password authentication"""
        try:
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
            
            self.log_connection_event('connection_attempt', f"Attempting password auth to {host}:{port}")
            
            self.client.connect(host, port=port, username=username, password=password, timeout=10)
            
            transport = self.client.get_transport()
            if transport:
                remote_key = transport.get_remote_server_key()
                verified, msg = self.verify_host_key(host, remote_key)
                if not verified:
                    self.log_connection_event('security_warning', msg)
            
            self.connected = True
            self.host = host
            self.username = username
            self.connection_type = 'remote'
            
            self.log_connection_event('connection_success', f"Connected to {host} as {username}")
            return True, f"Successfully connected to {host}"
        except paramiko.AuthenticationException:
            self.log_connection_event('authentication_failed', f"{host} - Invalid credentials")
            return False, "Authentication failed. Check username and password."
        except paramiko.SSHException as e:
            self.log_connection_event('connection_failed', f"{host} - SSH error: {str(e)}")
            return False, f"SSH connection failed: {str(e)}"
        except Exception as e:
            self.log_connection_event('connection_error', f"{host} - {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    def connect_with_key(self, host, port, username, key_data=None, key_file=None):
        """Connect to remote server using SSH key authentication"""
        try:
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
            
            self.log_connection_event('connection_attempt', f"Attempting key auth to {host}:{port}")
            
            if key_data:
                key_file_obj = StringIO(key_data)
                pkey = paramiko.RSAKey.from_private_key(key_file_obj)
                self.client.connect(host, port=port, username=username, pkey=pkey, timeout=10)
            elif key_file and os.path.exists(key_file):
                self.client.connect(host, port=port, username=username, key_filename=key_file, timeout=10)
            else:
                self.log_connection_event('connection_failed', "No valid SSH key provided")
                return False, "No valid SSH key provided"
            
            transport = self.client.get_transport()
            if transport:
                remote_key = transport.get_remote_server_key()
                verified, msg = self.verify_host_key(host, remote_key)
                if not verified:
                    self.log_connection_event('security_warning', msg)
            
            self.connected = True
            self.host = host
            self.username = username
            self.connection_type = 'remote'
            
            self.log_connection_event('connection_success', f"Connected to {host} as {username} (key auth)")
            return True, f"Successfully connected to {host} using SSH key"
        except paramiko.AuthenticationException:
            self.log_connection_event('authentication_failed', f"{host} - Invalid SSH key")
            return False, "Authentication failed. Check SSH key."
        except paramiko.SSHException as e:
            self.log_connection_event('connection_failed', f"{host} - SSH error: {str(e)}")
            return False, f"SSH connection failed: {str(e)}"
        except Exception as e:
            self.log_connection_event('connection_error', f"{host} - {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    def disconnect(self):
        """Disconnect from remote server"""
        if self.client:
            self.client.close()
            self.client = None
        self.connected = False
        self.host = None
        self.username = None
        self.connection_type = 'local'
    
    def execute_command(self, command):
        """Execute a command on the remote server and return output"""
        if not self.connected or not self.client:
            return None, "Not connected to remote server"
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            if error:
                return None, error
            return output, None
        except Exception as e:
            return None, f"Command execution error: {str(e)}"
    
    def get_connection_info(self):
        """Get current connection information"""
        if self.connection_type == 'local':
            return {
                'type': 'local',
                'host': 'localhost',
                'username': os.getenv('USER', 'current_user'),
                'connected': True
            }
        else:
            return {
                'type': 'remote',
                'host': self.host,
                'username': self.username,
                'connected': self.connected
            }
    
    def is_remote(self):
        """Check if currently monitoring a remote server"""
        return self.connection_type == 'remote' and self.connected
    
    def set_local(self):
        """Switch to local monitoring"""
        self.disconnect()
        self.connection_type = 'local'
    
    def verify_host_key(self, hostname, key):
        """Verify and store host key for security"""
        key_hash = hashlib.sha256(key.asbytes()).hexdigest()
        
        if hostname in self.host_keys:
            if self.host_keys[hostname] != key_hash:
                return False, "Host key mismatch - possible security threat"
        else:
            self.host_keys[hostname] = key_hash
        
        return True, "Host key verified"
    
    def get_connection_log(self):
        """Get connection history log"""
        return self.connection_log
    
    def log_connection_event(self, event_type, details):
        """Log connection events for security auditing"""
        from datetime import datetime
        
        self.connection_log.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'event': event_type,
            'details': details
        })
        
        if len(self.connection_log) > 100:
            self.connection_log = self.connection_log[-100:]
