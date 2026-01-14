from fpdf import FPDF
from datetime import datetime
import json
import os
import re

def clean_unicode_for_pdf(text):
    """Remove Unicode characters that aren't supported by standard PDF fonts"""
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
        clean_content = clean_unicode_for_pdf(content)
        self.multi_cell(0, 6, clean_content)
        self.ln()

    def subsection_title(self, title):
        """Add a subsection title"""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

class PDFExporter:
    """Export system information to PDF and store snapshots for comparison"""
    SNAPSHOT_FILE = "system_snapshot.json"

    def __init__(self, monitor, optimizer, device_manager, resource_monitor, security_manager):
        self.monitor = monitor
        self.optimizer = optimizer
        self.device_manager = device_manager
        self.resource_monitor = resource_monitor
        self.security_manager = security_manager

    # ===== Snapshot Handling =====
    def _get_snapshot(self):
        """Collect a full snapshot of all system metrics"""
        snapshot = {
            'cpu': self.monitor.get_cpu_usage(),
            'cpu_per_core': self.monitor.get_cpu_per_core(),
            'memory': self.monitor.get_memory_info(),
            'disk': self.monitor.get_disk_usage(),
            'network': self.monitor.get_network_activity(),
            'processes': self.monitor.get_processes(),
            'devices': self.device_manager.get_connected_devices(),
            'gpu': self.resource_monitor.get_gpu_info(),
            'battery': self.resource_monitor.get_battery_info(),
            'temperature': self.resource_monitor.get_temperature_sensors(),
            'security': self.security_manager.run_security_scan(),
            'timestamp': datetime.now().isoformat()
        }
        return snapshot

    def _load_previous_snapshot(self):
        """Load previous snapshot from file if exists"""
        if os.path.exists(self.SNAPSHOT_FILE):
            with open(self.SNAPSHOT_FILE, 'r') as f:
                return json.load(f)
        return None

    def _save_snapshot(self, snapshot):
        """Save snapshot to file"""
        with open(self.SNAPSHOT_FILE, 'w') as f:
            json.dump(snapshot, f, indent=2)

    def _compare_snapshots(self, old, new):
        """Compare old vs new snapshot and return differences"""
        diffs = {}
        for key in new:
            if key not in old:
                diffs[key] = {'old': None, 'new': new[key]}
            elif new[key] != old[key]:
                diffs[key] = {'old': old[key], 'new': new[key]}
        return diffs

    # ===== PDF Generation =====
    def generate_report(self, filename='system_report.pdf'):
        """Generate PDF report with snapshot comparison"""
        # Get today's snapshot
        today_snapshot = self._get_snapshot()

        # Load last snapshot
        last_snapshot = self._load_previous_snapshot()

        # Save today's snapshot for next week
        self._save_snapshot(today_snapshot)

        # Compare snapshots
        snapshot_diffs = {}
        if last_snapshot:
            snapshot_diffs = self._compare_snapshots(last_snapshot, today_snapshot)

        # Create PDF
        pdf = SystemReportPDF()
        pdf.add_page()

        # Add sections
        self._add_system_info(pdf, today_snapshot)
        self._add_cpu_memory_info(pdf, today_snapshot)
        self._add_disk_info(pdf, today_snapshot)
        self._add_network_info(pdf, today_snapshot)
        self._add_process_info(pdf, today_snapshot)
        self._add_device_info(pdf, today_snapshot)
        self._add_resource_info(pdf, today_snapshot)
        self._add_security_info(pdf, today_snapshot)
        
        # Add comparison sections
        if last_snapshot:
            self._add_comparison_summary(pdf, snapshot_diffs, last_snapshot, today_snapshot)
            self._add_overall_summary(pdf, snapshot_diffs)
        else:
            pdf.chapter_title("WEEKLY COMPARISON SUMMARY")
            pdf.chapter_body("No previous snapshot available for comparison. This is your first report.")

        # Save PDF
        pdf.output(filename)
        return filename

    # ===== PDF Sections =====
    def _add_system_info(self, pdf, snapshot):
        pdf.chapter_title('SYSTEM INFORMATION')
        content = f"Full system info is captured in snapshot.\nTimestamp: {snapshot['timestamp']}\n"
        pdf.chapter_body(content)

    def _add_cpu_memory_info(self, pdf, snapshot):
        pdf.chapter_title('CPU & MEMORY USAGE')
        cpu = snapshot['cpu']
        mem = snapshot['memory']
        cores = snapshot['cpu_per_core']

        content = f"Current CPU Usage: {cpu:.1f}%\n\nCPU Usage Per Core:\n"
        for i, core in enumerate(cores):
            content += f"  Core {i}: {core:.1f}%\n"

        content += f"\nMemory Usage:\n  Total: {mem['total_gb']:.2f} GB\n  Used: {mem['used_gb']:.2f} GB\n  Available: {mem['available_gb']:.2f} GB\n  Percent: {mem['percent']:.1f}%\n"
        pdf.chapter_body(content)

    def _add_disk_info(self, pdf, snapshot):
        pdf.chapter_title('DISK INFORMATION')
        for disk in snapshot['disk']:
            content = f"Device: {disk['device']}\nMount Point: {disk['mountpoint']}\nUsed: {disk['percent']:.1f}%\n"
            pdf.chapter_body(content)

    def _add_network_info(self, pdf, snapshot):
        pdf.chapter_title('NETWORK ACTIVITY')
        net = snapshot['network']
        content = f"Upload: {net['upload_speed']} B/s\nDownload: {net['download_speed']} B/s\n"
        pdf.chapter_body(content)

    def _add_process_info(self, pdf, snapshot):
        pdf.chapter_title('TOP PROCESSES')
        content = ""
        for proc in snapshot['processes'][:20]:
            clean_name = clean_unicode_for_pdf(proc['name'])
            content += f"{proc['pid']:<8}{clean_name[:28].ljust(28)} {proc['cpu_percent']:>6.1f}% {proc['memory_percent']:>6.1f}% {proc['status']}\n"
        pdf.set_font('Courier', '', 9)
        pdf.multi_cell(0, 5, content)
        pdf.ln()

    def _add_device_info(self, pdf, snapshot):
        pdf.chapter_title('CONNECTED DEVICES')
        devices = snapshot['devices']
        content = ""
        for d in devices:
            removable = "Yes" if d['removable'] else "No"
            content += f"{d['device']} mounted at {d['mountpoint']} ({d['fstype']}), Removable: {removable}\n"
        if not devices:
            content = "No devices detected.\n"
        pdf.chapter_body(content)

    def _add_resource_info(self, pdf, snapshot):
        pdf.chapter_title('ADVANCED RESOURCES')
        content = ""
        for gpu in snapshot['gpu']:
            content += f"GPU: {gpu['name']} Load: {gpu['load']}% Memory: {gpu['memory_used']}/{gpu['memory_total']} MB Temp: {gpu['temperature']} C\n"
        battery = snapshot['battery']
        content += f"Battery: {battery['percent']}% {'Plugged In' if battery['power_plugged'] else 'On Battery'}\n"
        pdf.chapter_body(content)

    def _add_security_info(self, pdf, snapshot):
        pdf.chapter_title('SECURITY OVERVIEW')
        sec = snapshot['security']
        content = f"Score: {sec['security_score']}/100\nOpen Ports: {sec['open_ports']}\n"
        pdf.chapter_body(content)

    # ===== FIXED: Comparison Section =====
    def _add_comparison_summary(self, pdf, diffs, old_snapshot, new_snapshot):
        pdf.chapter_title("WEEKLY COMPARISON SUMMARY")
        
        if not diffs:
            pdf.chapter_body("No significant changes detected since last snapshot.")
            return

        # Calculate time difference
        old_time = datetime.fromisoformat(old_snapshot['timestamp'])
        new_time = datetime.fromisoformat(new_snapshot['timestamp'])
        time_diff = new_time - old_time
        days_diff = time_diff.days
        
        intro = f"Comparison between snapshots taken {days_diff} days apart.\n"
        intro += f"Previous: {old_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        intro += f"Current:  {new_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        pdf.chapter_body(intro)

        # CPU Comparison
        if 'cpu' in diffs:
            pdf.subsection_title("CPU Usage Changes")
            old_val = diffs['cpu']['old']
            new_val = diffs['cpu']['new']
            delta = new_val - old_val
            status = "increased" if delta > 0 else "decreased" if delta < 0 else "unchanged"
            
            content = f"Overall CPU Usage: {old_val:.1f}% -> {new_val:.1f}%\n"
            content += f"Change: {abs(delta):.1f}% ({status})\n"
            
            if 'cpu_per_core' in diffs:
                content += "\nPer-Core Changes:\n"
                for i, (o, n) in enumerate(zip(diffs['cpu_per_core']['old'], diffs['cpu_per_core']['new'])):
                    core_delta = n - o
                    if abs(core_delta) > 1.0:  # Only show significant changes
                        core_status = "UP" if core_delta > 0 else "DOWN"
                        content += f"  Core {i}: {o:.1f}% -> {n:.1f}% ({core_status} {abs(core_delta):.1f}%)\n"
            
            pdf.chapter_body(content)

        # Memory Comparison
        if 'memory' in diffs:
            pdf.subsection_title("Memory Usage Changes")
            old_mem = diffs['memory']['old']
            new_mem = diffs['memory']['new']
            
            content = f"Total Memory: {old_mem['total_gb']:.2f} GB -> {new_mem['total_gb']:.2f} GB\n"
            content += f"Used Memory: {old_mem['used_gb']:.2f} GB -> {new_mem['used_gb']:.2f} GB\n"
            
            used_delta = new_mem['used_gb'] - old_mem['used_gb']
            used_status = "increased" if used_delta > 0 else "decreased"
            content += f"Change: {abs(used_delta):.2f} GB ({used_status})\n\n"
            
            content += f"Available Memory: {old_mem['available_gb']:.2f} GB -> {new_mem['available_gb']:.2f} GB\n"
            content += f"Usage Percentage: {old_mem['percent']:.1f}% -> {new_mem['percent']:.1f}%\n"
            
            pdf.chapter_body(content)

        # Disk Comparison
        if 'disk' in diffs:
            pdf.subsection_title("Disk Usage Changes")
            old_disks = diffs['disk']['old']
            new_disks = diffs['disk']['new']
            
            for o_disk, n_disk in zip(old_disks, new_disks):
                mount = n_disk['mountpoint']
                content = f"Drive: {mount}\n"
                content += f"  Used: {o_disk['used_gb']:.2f} GB -> {n_disk['used_gb']:.2f} GB\n"
                
                used_delta = n_disk['used_gb'] - o_disk['used_gb']
                content += f"  Change: {abs(used_delta):.2f} GB "
                content += f"({'more' if used_delta > 0 else 'less'} used)\n"
                
                content += f"  Free: {o_disk['free_gb']:.2f} GB -> {n_disk['free_gb']:.2f} GB\n"
                content += f"  Usage: {o_disk['percent']:.1f}% -> {n_disk['percent']:.1f}%\n\n"
                
                pdf.chapter_body(content)

        # Network Comparison
        if 'network' in diffs:
            pdf.subsection_title("Network Activity Changes")
            old_net = diffs['network']['old']
            new_net = diffs['network']['new']
            
            content = f"Upload Speed: {old_net['upload_speed']} B/s -> {new_net['upload_speed']} B/s\n"
            content += f"Download Speed: {old_net['download_speed']} B/s -> {new_net['download_speed']} B/s\n"
            
            pdf.chapter_body(content)

        # Battery Comparison
        if 'battery' in diffs:
            pdf.subsection_title("Battery Status Changes")
            old_bat = diffs['battery']['old']
            new_bat = diffs['battery']['new']
            
            content = f"Battery Level: {old_bat['percent']:.1f}% -> {new_bat['percent']:.1f}%\n"
            
            delta_bat = new_bat['percent'] - old_bat['percent']
            if abs(delta_bat) > 5:
                status = "charged" if delta_bat > 0 else "discharged"
                content += f"Change: {abs(delta_bat):.1f}% ({status})\n"
            
            old_plugged = "Yes" if old_bat['power_plugged'] else "No"
            new_plugged = "Yes" if new_bat['power_plugged'] else "No"
            content += f"Power Plugged: {old_plugged} -> {new_plugged}\n"
            
            pdf.chapter_body(content)

        # Security Comparison
        if 'security' in diffs:
            pdf.subsection_title("Security Status Changes")
            old_sec = diffs['security']['old']
            new_sec = diffs['security']['new']
            
            content = f"Security Score: {old_sec['security_score']}/100 -> {new_sec['security_score']}/100\n"
            
            score_delta = new_sec['security_score'] - old_sec['security_score']
            if score_delta != 0:
                status = "improved" if score_delta > 0 else "declined"
                content += f"Change: {abs(score_delta)} points ({status})\n"
            
            content += f"Open Ports: {len(old_sec['open_ports'])} -> {len(new_sec['open_ports'])}\n"
            
            pdf.chapter_body(content)

    # ===== FIXED: Overall Summary =====
    def _add_overall_summary(self, pdf, diffs):
        pdf.chapter_title("EXECUTIVE SUMMARY")
        
        if not diffs:
            pdf.chapter_body("System status remains stable with no significant changes.")
            return

        summary_points = []
        
        # CPU Summary
        if 'cpu' in diffs:
            delta = diffs['cpu']['new'] - diffs['cpu']['old']
            if abs(delta) > 5:
                trend = "increased" if delta > 0 else "decreased"
                summary_points.append(f"CPU usage {trend} by {abs(delta):.1f}%")
        
        # Memory Summary
        if 'memory' in diffs:
            delta_used = diffs['memory']['new']['used_gb'] - diffs['memory']['old']['used_gb']
            delta_percent = diffs['memory']['new']['percent'] - diffs['memory']['old']['percent']
            if abs(delta_percent) > 5:
                trend = "increased" if delta_percent > 0 else "decreased"
                summary_points.append(f"Memory usage {trend} by {abs(delta_used):.2f} GB ({abs(delta_percent):.1f}%)")
        
        # Disk Summary
        if 'disk' in diffs:
            total_delta_used = sum(n['used_gb'] for n in diffs['disk']['new']) - sum(o['used_gb'] for o in diffs['disk']['old'])
            if abs(total_delta_used) > 1:
                trend = "increased" if total_delta_used > 0 else "decreased"
                summary_points.append(f"Total disk usage {trend} by {abs(total_delta_used):.2f} GB")
        
        # Battery Summary
        if 'battery' in diffs:
            delta_battery = diffs['battery']['new']['percent'] - diffs['battery']['old']['percent']
            if abs(delta_battery) > 10:
                trend = "charged" if delta_battery > 0 else "discharged"
                summary_points.append(f"Battery {trend} by {abs(delta_battery):.1f}%")
        
        # Security Summary
        if 'security' in diffs:
            delta_score = diffs['security']['new']['security_score'] - diffs['security']['old']['security_score']
            if delta_score != 0:
                trend = "improved" if delta_score > 0 else "declined"
                summary_points.append(f"Security score {trend} by {abs(delta_score)} points")
        
        # Build summary text
        if summary_points:
            content = "Key Changes:\n\n"
            for i, point in enumerate(summary_points, 1):
                content += f"{i}. {point}\n"
            
            content += "\n\nRecommendations:\n"
            
            # Add recommendations based on changes
            if 'cpu' in diffs and diffs['cpu']['new'] > 80:
                content += "- High CPU usage detected. Consider closing unnecessary applications.\n"
            
            if 'memory' in diffs and diffs['memory']['new']['percent'] > 85:
                content += "- Memory usage is high. Consider upgrading RAM or closing applications.\n"
            
            if 'disk' in diffs:
                for disk in diffs['disk']['new']:
                    if disk['percent'] > 85:
                        content += f"- Disk {disk['mountpoint']} is running low on space. Clean up files.\n"
            
            if 'security' in diffs and diffs['security']['new']['security_score'] < 70:
                content += "- Security score is below optimal. Review open ports and firewall settings.\n"
            
            if not any(['cpu' in diffs and diffs['cpu']['new'] > 80,
                       'memory' in diffs and diffs['memory']['new']['percent'] > 85,
                       'security' in diffs and diffs['security']['new']['security_score'] < 70]):
                content += "- System is operating within normal parameters.\n"
        else:
            content = "No significant changes detected. System is stable.\n"
        
        pdf.chapter_body(content)
