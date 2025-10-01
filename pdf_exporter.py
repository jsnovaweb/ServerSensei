from fpdf import FPDF
from datetime import datetime
import platform
import re

def clean_unicode_for_pdf(text):
    """Remove Unicode characters that aren't supported by standard PDF fonts"""
    # Replace common Unicode characters with text equivalents
    replacements = {
        '⚠️': '[!]',
        '⚠': '[!]',
        '✓': '[OK]',
        '✅': '[OK]',
        '❌': '[X]',
        '🔒': '[LOCK]',
        '🔓': '[UNLOCK]',
        '📍': '[PIN]',
        '📡': '[SIGNAL]',
        '↑': 'UP',
        '↓': 'DOWN',
        '°': ' deg',
        '→': '->',
        '←': '<-',
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text

class SystemReportPDF(FPDF):
    """PDF Report Generator for System Monitor"""
    
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'System Monitor & Optimizer Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(4)
    
    def chapter_body(self, content):
        self.set_font('Arial', '', 11)
        # Clean Unicode characters for PDF compatibility
        clean_content = clean_unicode_for_pdf(content)
        self.multi_cell(0, 6, clean_content)
        self.ln()

class PDFExporter:
    """Export system information to PDF"""
    
    def __init__(self, monitor, optimizer, device_manager, resource_monitor, security_manager):
        self.monitor = monitor
        self.optimizer = optimizer
        self.device_manager = device_manager
        self.resource_monitor = resource_monitor
        self.security_manager = security_manager
    
    def generate_report(self, filename='system_report.pdf'):
        """Generate a comprehensive system report PDF"""
        pdf = SystemReportPDF()
        pdf.add_page()
        
        self._add_system_info(pdf)
        self._add_cpu_memory_info(pdf)
        self._add_disk_info(pdf)
        self._add_network_info(pdf)
        self._add_process_info(pdf)
        self._add_device_info(pdf)
        self._add_resource_info(pdf)
        self._add_security_info(pdf)
        
        pdf.output(filename)
        return filename
    
    def _add_system_info(self, pdf):
        """Add system information section"""
        pdf.chapter_title('SYSTEM INFORMATION')
        
        info = self.monitor.get_system_info()
        
        content = f"""Operating System: {info['os']}
OS Version: {info['os_version']}
OS Release: {info['os_release']}
Architecture: {info['architecture']}
Processor: {info['processor']}
Hostname: {info['hostname']}
CPU Cores (Physical): {info['cpu_count']}
CPU Cores (Logical): {info['cpu_count_logical']}
Boot Time: {info['boot_time']}
Uptime: {info['uptime']}"""
        
        pdf.chapter_body(content)
    
    def _add_cpu_memory_info(self, pdf):
        """Add CPU and memory information"""
        pdf.chapter_title('CPU & MEMORY USAGE')
        
        cpu = self.monitor.get_cpu_usage()
        mem = self.monitor.get_memory_info()
        cpu_cores = self.monitor.get_cpu_per_core()
        
        content = f"""Current CPU Usage: {cpu:.1f}%

CPU Usage Per Core:
"""
        for i, core_usage in enumerate(cpu_cores):
            content += f"  Core {i}: {core_usage:.1f}%\n"
        
        content += f"""
Memory Information:
  Total RAM: {mem['total_gb']:.2f} GB
  Used RAM: {mem['used_gb']:.2f} GB
  Available RAM: {mem['available_gb']:.2f} GB
  Memory Usage: {mem['percent']:.1f}%"""
        
        pdf.chapter_body(content)
    
    def _add_disk_info(self, pdf):
        """Add disk information"""
        pdf.chapter_title('DISK INFORMATION')
        
        disks = self.monitor.get_disk_usage()
        
        content = ""
        for disk in disks:
            content += f"""Device: {disk['device']}
  Mount Point: {disk['mountpoint']}
  File System: {disk['fstype']}
  Total: {disk['total_gb']:.2f} GB
  Used: {disk['used_gb']:.2f} GB ({disk['percent']:.1f}%)
  Free: {disk['free_gb']:.2f} GB

"""
        
        pdf.chapter_body(content)
    
    def _add_network_info(self, pdf):
        """Add network information"""
        pdf.chapter_title('NETWORK ACTIVITY')
        
        net = self.monitor.get_network_activity()
        
        content = f"""Current Network Activity:
  Upload Speed: {net['upload_speed']/1024:.2f} KB/s ({net['upload_speed_mb']:.2f} MB/s)
  Download Speed: {net['download_speed']/1024:.2f} KB/s ({net['download_speed_mb']:.2f} MB/s)
  Total Bytes Sent: {net['bytes_sent'] / (1024**3):.2f} GB
  Total Bytes Received: {net['bytes_recv'] / (1024**3):.2f} GB"""
        
        pdf.chapter_body(content)
    
    def _add_process_info(self, pdf):
        """Add top processes information"""
        pdf.chapter_title('TOP PROCESSES (by CPU usage)')
        
        processes = self.monitor.get_processes()
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        content = "PID     Name                           CPU%    Memory%    Status\n"
        content += "-" * 70 + "\n"
        
        for proc in processes[:20]:
            # Clean process name to remove Unicode characters
            clean_name = clean_unicode_for_pdf(proc['name'])[:28].ljust(28)
            clean_status = clean_unicode_for_pdf(proc['status'])
            content += f"{proc['pid']:<8}{clean_name}  {proc['cpu_percent']:>6.1f}  {proc['memory_percent']:>8.1f}  {clean_status}\n"
        
        pdf.set_font('Courier', '', 9)
        # Clean the entire content before adding to PDF
        clean_content = clean_unicode_for_pdf(content)
        pdf.multi_cell(0, 5, clean_content)
        pdf.ln()
    
    def _add_device_info(self, pdf):
        """Add connected devices information"""
        pdf.chapter_title('CONNECTED DEVICES')
        
        devices = self.device_manager.get_connected_devices()
        
        content = ""
        for device in devices:
            removable = "Yes" if device['removable'] else "No"
            content += f"""Device: {device['device']}
  Mount Point: {device['mountpoint']}
  Type: {device['fstype']}
  Total: {device['total_gb']:.2f} GB
  Used: {device['used_gb']:.2f} GB ({device['percent']:.1f}%)
  Free: {device['free_gb']:.2f} GB
  Removable: {removable}

"""
        
        if not devices:
            content = "No devices detected\n"
        
        pdf.chapter_body(content)
    
    def _add_resource_info(self, pdf):
        """Add advanced resource information"""
        pdf.chapter_title('ADVANCED RESOURCES')
        
        content = ""
        
        gpu_info = self.resource_monitor.get_gpu_info()
        content += "GPU Information:\n"
        for gpu in gpu_info:
            content += f"""  GPU #{gpu['id']}: {gpu['name']}
    Load: {gpu['load']:.1f}%
    Memory: {gpu['memory_used']:.0f} MB / {gpu['memory_total']:.0f} MB ({gpu['memory_percent']:.1f}%)
    Temperature: {gpu['temperature']:.1f} C

"""
        
        battery_info = self.resource_monitor.get_battery_info()
        content += "Battery Information:\n"
        if battery_info['present']:
            status = 'Plugged In' if battery_info['power_plugged'] else 'On Battery'
            content += f"""  Battery Level: {battery_info['percent']:.1f}%
  Power Status: {status}
  Time Remaining: {battery_info['time_left']}
  Health: {battery_info['health']}

"""
        else:
            content += "  No battery detected (Desktop system)\n\n"
        
        temps = self.resource_monitor.get_temperature_sensors()
        content += "Temperature Sensors:\n"
        for temp in temps[:10]:
            temp_info = f"  {temp['sensor']} - {temp['label']}: {temp['current']:.1f} C"
            if temp['high'] > 0:
                temp_info += f" (High: {temp['high']:.1f} C, Critical: {temp['critical']:.1f} C)"
            content += temp_info + "\n"
        
        pdf.chapter_body(content)
    
    def _add_security_info(self, pdf):
        """Add security scan information"""
        pdf.chapter_title('SECURITY OVERVIEW')
        
        results = self.security_manager.run_security_scan()
        
        content = f"""Security Scan Results:
Timestamp: {results['timestamp']}
Security Score: {results['security_score']}/100

"""
        
        if results['security_score'] >= 80:
            content += "Status: [EXCELLENT] EXCELLENT SECURITY\n\n"
        elif results['security_score'] >= 60:
            content += "Status: [GOOD] GOOD SECURITY (Some improvements needed)\n\n"
        else:
            content += "Status: [WARNING] POOR SECURITY (Immediate action required)\n\n"
        
        content += "Open Ports:\n"
        content += f"  Total: {results['open_ports']['total']}\n"
        if results['open_ports']['suspicious']:
            content += f"  Suspicious: {len(results['open_ports']['suspicious'])}\n"
        
        content += "\nFirewall Status:\n"
        content += f"  Status: {results['firewall_status']['status']}\n"
        content += f"  Details: {results['firewall_status']['details']}\n"
        
        if results['warnings']:
            content += "\nWarnings:\n"
            for warning in results['warnings']:
                content += f"  - {warning}\n"
        
        if results['recommendations']:
            content += "\nRecommendations:\n"
            for rec in results['recommendations']:
                content += f"  - {rec}\n"
        
        pdf.chapter_body(content)
