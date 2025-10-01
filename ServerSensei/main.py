#!/usr/bin/env python3
import os
import sys
from datetime import datetime


# Check if display is available
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    if 'DISPLAY' not in os.environ and 'WAYLAND_DISPLAY' not in os.environ:
        print("=" * 70)
        print("SERVER MONITOR & OPTIMIZER - Desktop GUI Application")
        print("=" * 70)
        print("\n⚠️  No graphical display detected!")
        print("\nThis is a desktop GUI application. To use it:")
        print("  • Run on a machine with a desktop environment")
        print("  • Use VNC or remote desktop")
        print("  • Enable X11 forwarding over SSH")
        print("\nAll backend modules are ready.")
        print("=" * 70)
        sys.exit(0)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from dependency_installer import check_and_install_dependencies

check_and_install_dependencies()

from system_monitor import SystemMonitor
from optimizer import SystemOptimizer
from device_manager import DeviceManager
from ssh_manager import SSHConnectionManager
from remote_monitor import RemoteSystemMonitor
from connection_dialog import ConnectionDialog
from resource_monitor import ResourceMonitor
from security_manager import SecurityManager
from pdf_exporter import PDFExporter
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

print("Starting Server Monitor GUI...")
print("Note: In headless environments, this will run but won't display a window.")
print("The application is designed for desktop use.")

class SystemMonitorApp:
    """Main application class for the System Monitor & Optimizer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Cross-Platform Server Monitor & Optimizer")
        self.root.geometry("1200x800")
        
        self.ssh_manager = SSHConnectionManager()
        self.local_monitor = SystemMonitor()
        self.remote_monitor = RemoteSystemMonitor(self.ssh_manager)
        self.monitor = self.local_monitor
        
        self.optimizer = SystemOptimizer()
        self.device_manager = DeviceManager()
        self.resource_monitor = ResourceMonitor()
        self.security_manager = SecurityManager()
        
        self.pdf_exporter = PDFExporter(
            self.monitor,
            self.optimizer,
            self.device_manager,
            self.resource_monitor,
            self.security_manager
        )
        
        self.cpu_history = deque(maxlen=50)
        self.ram_history = deque(maxlen=50)
        self.net_upload_history = deque(maxlen=50)
        self.net_download_history = deque(maxlen=50)
        
        self.running = True
        self.monitoring_mode = 'local'
        
        self.create_menu()
        self.create_widgets()
        self.start_monitoring()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to PDF", command=self.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        connection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Connection", menu=connection_menu)
        connection_menu.add_command(label="Connection Settings", command=self.show_connection_dialog)
        connection_menu.add_separator()
        connection_menu.add_command(label="Disconnect", command=self.disconnect_remote)
    
    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        self.connection_label = ttk.Label(top_frame, text="📍 Monitoring: Local Server", font=('Arial', 10, 'bold'), foreground='green')
        self.connection_label.pack(side='left', padx=10)
        
        ttk.Button(top_frame, text="Change Connection", command=self.show_connection_dialog).pack(side='right', padx=10)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.dashboard_tab = ttk.Frame(notebook)
        self.processes_tab = ttk.Frame(notebook)
        self.optimize_tab = ttk.Frame(notebook)
        self.devices_tab = ttk.Frame(notebook)
        self.resources_tab = ttk.Frame(notebook)
        self.security_tab = ttk.Frame(notebook)
        self.sysinfo_tab = ttk.Frame(notebook)
        
        notebook.add(self.dashboard_tab, text='Dashboard')
        notebook.add(self.processes_tab, text='Processes')
        notebook.add(self.optimize_tab, text='Optimize')
        notebook.add(self.devices_tab, text='Devices')
        notebook.add(self.resources_tab, text='Resources')
        notebook.add(self.security_tab, text='Security')
        notebook.add(self.sysinfo_tab, text='System Info')
        
        self.create_dashboard_tab()
        self.create_processes_tab()
        self.create_optimize_tab()
        self.create_devices_tab()
        self.create_resources_tab()
        self.create_security_tab()
        self.create_sysinfo_tab()
    
    def create_dashboard_tab(self):
        main_frame = ttk.Frame(self.dashboard_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        stats_frame = ttk.LabelFrame(main_frame, text="Current Stats", padding=10)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.cpu_label = ttk.Label(stats_frame, text="CPU: 0%", font=('Arial', 12))
        self.cpu_label.grid(row=0, column=0, padx=10, sticky='w')
        
        self.ram_label = ttk.Label(stats_frame, text="RAM: 0%", font=('Arial', 12))
        self.ram_label.grid(row=0, column=1, padx=10, sticky='w')
        
        self.disk_label = ttk.Label(stats_frame, text="Disk: 0%", font=('Arial', 12))
        self.disk_label.grid(row=0, column=2, padx=10, sticky='w')
        
        self.net_label = ttk.Label(stats_frame, text="Network: ↑0 KB/s ↓0 KB/s", font=('Arial', 12))
        self.net_label.grid(row=0, column=3, padx=10, sticky='w')
        
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(fill='both', expand=True)
        
        self.fig = Figure(figsize=(12, 6))
        
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.fig.tight_layout(pad=3.0)
    
    def create_processes_tab(self):
        main_frame = ttk.Frame(self.processes_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="Refresh Processes", command=self.refresh_processes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Kill Selected Process", command=self.kill_selected_process).pack(side='left', padx=5)
        
        columns = ('PID', 'Name', 'CPU %', 'Memory %', 'Status')
        self.process_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.process_tree.heading(col, text=col, command=lambda c=col: self.sort_processes(c))
            self.process_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.refresh_processes()
    
    def create_optimize_tab(self):
        main_frame = ttk.Frame(self.optimize_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = ttk.LabelFrame(main_frame, text="Optimization Tools", padding=10)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="Clear Temp Files", command=self.clear_temp_files, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Free Memory", command=self.free_memory, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Kill Unresponsive Processes", command=self.kill_unresponsive, width=20).pack(pady=5)
        ttk.Button(button_frame, text="🚀 Quick Optimize (All)", command=self.quick_optimize, width=20).pack(pady=10)
        
        results_frame = ttk.LabelFrame(main_frame, text="Optimization Results", padding=10)
        results_frame.pack(fill='both', expand=True)
        
        self.optimize_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.optimize_text.pack(fill='both', expand=True)
    
    def create_devices_tab(self):
        main_frame = ttk.Frame(self.devices_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="Refresh Devices", command=self.refresh_devices).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Eject Selected Device", command=self.eject_selected_device).pack(side='left', padx=5)
        
        columns = ('Device', 'Mount Point', 'Type', 'Total (GB)', 'Used (GB)', 'Free (GB)', 'Usage %', 'Removable')
        self.device_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.device_tree.heading(col, text=col)
            if col in ['Total (GB)', 'Used (GB)', 'Free (GB)']:
                self.device_tree.column(col, width=100)
            else:
                self.device_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        self.device_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.refresh_devices()
    
    def create_resources_tab(self):
        main_frame = ttk.Frame(self.resources_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="Refresh Resource Data", command=self.refresh_resources).pack(side='left', padx=5)
        
        self.resources_text = scrolledtext.ScrolledText(main_frame, height=30, width=100)
        self.resources_text.pack(fill='both', expand=True)
        
        self.refresh_resources()
    
    def create_security_tab(self):
        main_frame = ttk.Frame(self.security_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="Run Security Scan", command=self.run_security_scan).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Open Ports", command=self.view_open_ports).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Check Firewall", command=self.check_firewall).pack(side='left', padx=5)
        
        self.security_text = scrolledtext.ScrolledText(main_frame, height=30, width=100)
        self.security_text.pack(fill='both', expand=True)
        
        self.security_text.insert('end', "Click 'Run Security Scan' to perform a comprehensive security check.\n\n")
    
    def create_sysinfo_tab(self):
        main_frame = ttk.Frame(self.sysinfo_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding=10)
        info_frame.pack(fill='both', expand=True)
        
        self.sysinfo_text = scrolledtext.ScrolledText(info_frame, height=30, width=100)
        self.sysinfo_text.pack(fill='both', expand=True)
        
        self.refresh_sysinfo()
    
    def update_dashboard(self):
        cpu = self.monitor.get_cpu_usage()
        mem = self.monitor.get_memory_info()
        net = self.monitor.get_network_activity()
        disk = self.monitor.get_disk_usage()
        
        self.cpu_history.append(cpu)
        self.ram_history.append(mem['percent'])
        self.net_upload_history.append(net['upload_speed'] / 1024)
        self.net_download_history.append(net['download_speed'] / 1024)
        
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
        self.ram_label.config(text=f"RAM: {mem['percent']:.1f}% ({mem['used_gb']:.1f}/{mem['total_gb']:.1f} GB)")
        
        if disk:
            disk_percent = disk[0]['percent']
            self.disk_label.config(text=f"Disk: {disk_percent:.1f}%")
        
        self.net_label.config(text=f"Network: ↑{net['upload_speed']/1024:.1f} KB/s ↓{net['download_speed']/1024:.1f} KB/s")
        
        self.ax1.clear()
        self.ax1.plot(list(self.cpu_history), color='blue')
        self.ax1.set_title('CPU Usage (%)')
        self.ax1.set_ylim(0, 100)
        self.ax1.grid(True)
        
        self.ax2.clear()
        self.ax2.plot(list(self.ram_history), color='green')
        self.ax2.set_title('RAM Usage (%)')
        self.ax2.set_ylim(0, 100)
        self.ax2.grid(True)
        
        self.ax3.clear()
        self.ax3.plot(list(self.net_upload_history), color='red', label='Upload')
        self.ax3.set_title('Network Upload (KB/s)')
        self.ax3.grid(True)
        self.ax3.legend()
        
        self.ax4.clear()
        self.ax4.plot(list(self.net_download_history), color='purple', label='Download')
        self.ax4.set_title('Network Download (KB/s)')
        self.ax4.grid(True)
        self.ax4.legend()
        
        self.canvas.draw()
    
    def refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        processes = self.monitor.get_processes()
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        for proc in processes[:100]:
            self.process_tree.insert('', 'end', values=(
                proc['pid'],
                proc['name'],
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_percent']:.1f}",
                proc['status']
            ))
    
    def sort_processes(self, column):
        self.refresh_processes()
    
    def kill_selected_process(self):
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to kill")
            return
        
        item = self.process_tree.item(selection[0])
        pid = int(item['values'][0])
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Kill process {name} (PID: {pid})?"):
            success, message = self.monitor.kill_process(pid)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_processes()
            else:
                messagebox.showerror("Error", message)
    
    def clear_temp_files(self):
        self.optimize_text.insert('end', "Clearing temporary files...\n")
        self.optimize_text.see('end')
        self.root.update()
        
        results = self.optimizer.clear_temp_files()
        
        for result in results:
            if 'error' in result:
                self.optimize_text.insert('end', f"Error in {result['directory']}: {result['error']}\n")
            else:
                self.optimize_text.insert('end', 
                    f"Cleaned {result['directory']}: {result['files_deleted']} files, "
                    f"{result['space_freed_mb']:.2f} MB freed\n")
        
        self.optimize_text.insert('end', "\nTemp file cleanup complete!\n\n")
        self.optimize_text.see('end')
    
    def free_memory(self):
        self.optimize_text.insert('end', "Freeing memory...\n")
        self.optimize_text.see('end')
        self.root.update()
        
        result = self.optimizer.free_memory()
        
        self.optimize_text.insert('end', 
            f"Memory freed: {result['freed_mb']:.2f} MB\n"
            f"Available before: {result['before_available_mb']:.2f} MB\n"
            f"Available after: {result['after_available_mb']:.2f} MB\n\n")
        self.optimize_text.see('end')
    
    def kill_unresponsive(self):
        self.optimize_text.insert('end', "Terminating unresponsive processes...\n")
        self.optimize_text.see('end')
        self.root.update()
        
        results = self.optimizer.kill_unresponsive_processes()
        
        if results:
            for proc in results:
                self.optimize_text.insert('end', 
                    f"Terminated: {proc['name']} (PID: {proc['pid']}, Status: {proc['status']})\n")
        else:
            self.optimize_text.insert('end', "No unresponsive processes found\n")
        
        self.optimize_text.insert('end', "\nUnresponsive process cleanup complete!\n\n")
        self.optimize_text.see('end')
    
    def quick_optimize(self):
        self.optimize_text.insert('end', "=== QUICK OPTIMIZE ===\n\n")
        self.optimize_text.see('end')
        self.root.update()
        
        results = self.optimizer.quick_optimize()
        summary = self.optimizer.get_optimization_summary(results)
        
        for line in summary:
            self.optimize_text.insert('end', f"✓ {line}\n")
        
        self.optimize_text.insert('end', "\n=== OPTIMIZATION COMPLETE ===\n\n")
        self.optimize_text.see('end')
        
        messagebox.showinfo("Optimization Complete", "Quick optimization finished successfully!")
    
    def refresh_devices(self):
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        devices = self.device_manager.get_connected_devices()
        
        for device in devices:
            self.device_tree.insert('', 'end', values=(
                device['device'],
                device['mountpoint'],
                device['fstype'],
                f"{device['total_gb']:.2f}",
                f"{device['used_gb']:.2f}",
                f"{device['free_gb']:.2f}",
                f"{device['percent']:.1f}",
                "Yes" if device['removable'] else "No"
            ))
    
    def eject_selected_device(self):
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device to eject")
            return
        
        item = self.device_tree.item(selection[0])
        mountpoint = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Eject device at {mountpoint}?"):
            success, message = self.device_manager.eject_device(mountpoint)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_devices()
            else:
                messagebox.showerror("Error", message)
    
    def refresh_sysinfo(self):
        self.sysinfo_text.delete('1.0', 'end')
        
        info = self.monitor.get_system_info()
        
        self.sysinfo_text.insert('end', "=== SYSTEM INFORMATION ===\n\n")
        self.sysinfo_text.insert('end', f"Operating System: {info['os']}\n")
        self.sysinfo_text.insert('end', f"OS Version: {info['os_version']}\n")
        self.sysinfo_text.insert('end', f"OS Release: {info['os_release']}\n")
        self.sysinfo_text.insert('end', f"Architecture: {info['architecture']}\n")
        self.sysinfo_text.insert('end', f"Processor: {info['processor']}\n")
        self.sysinfo_text.insert('end', f"Hostname: {info['hostname']}\n")
        self.sysinfo_text.insert('end', f"CPU Cores (Physical): {info['cpu_count']}\n")
        self.sysinfo_text.insert('end', f"CPU Cores (Logical): {info['cpu_count_logical']}\n")
        self.sysinfo_text.insert('end', f"Boot Time: {info['boot_time']}\n")
        self.sysinfo_text.insert('end', f"Uptime: {info['uptime']}\n\n")
        
        mem = self.monitor.get_memory_info()
        self.sysinfo_text.insert('end', "=== MEMORY INFORMATION ===\n\n")
        self.sysinfo_text.insert('end', f"Total RAM: {mem['total_gb']:.2f} GB\n")
        self.sysinfo_text.insert('end', f"Used RAM: {mem['used_gb']:.2f} GB\n")
        self.sysinfo_text.insert('end', f"Available RAM: {mem['available_gb']:.2f} GB\n")
        self.sysinfo_text.insert('end', f"Usage: {mem['percent']:.1f}%\n\n")
        
        disks = self.monitor.get_disk_usage()
        self.sysinfo_text.insert('end', "=== DISK INFORMATION ===\n\n")
        for disk in disks:
            self.sysinfo_text.insert('end', f"Device: {disk['device']}\n")
            self.sysinfo_text.insert('end', f"  Mount: {disk['mountpoint']}\n")
            self.sysinfo_text.insert('end', f"  Type: {disk['fstype']}\n")
            self.sysinfo_text.insert('end', f"  Total: {disk['total_gb']:.2f} GB\n")
            self.sysinfo_text.insert('end', f"  Used: {disk['used_gb']:.2f} GB ({disk['percent']:.1f}%)\n")
            self.sysinfo_text.insert('end', f"  Free: {disk['free_gb']:.2f} GB\n\n")
    
    def start_monitoring(self):
        def monitor_loop():
            if self.running:
                try:
                    self.update_dashboard()
                except:
                    pass
                self.root.after(2000, monitor_loop)
        
        self.root.after(100, monitor_loop)
    
    def show_connection_dialog(self):
        dialog = ConnectionDialog(self.root)
        
        if dialog.result:
            if dialog.result['type'] == 'local':
                self.disconnect_remote()
            else:
                self.connect_remote(dialog.result)
    
    def connect_remote(self, connection_info):
        try:
            if connection_info['auth_method'] == 'password':
                success, message = self.ssh_manager.connect_with_password(
                    connection_info['host'],
                    connection_info['port'],
                    connection_info['username'],
                    connection_info['password']
                )
            else:
                success, message = self.ssh_manager.connect_with_key(
                    connection_info['host'],
                    connection_info['port'],
                    connection_info['username'],
                    key_data=connection_info.get('key_data'),
                    key_file=connection_info.get('key_file')
                )
            
            if success:
                self.monitor = self.remote_monitor
                self.monitoring_mode = 'remote'
                self.connection_label.config(
                    text=f"📡 Monitoring: {connection_info['host']} (Remote)",
                    foreground='blue'
                )
                messagebox.showinfo("Success", message)
                
                self.cpu_history.clear()
                self.ram_history.clear()
                self.net_upload_history.clear()
                self.net_download_history.clear()
            else:
                messagebox.showerror("Connection Failed", message)
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def disconnect_remote(self):
        self.ssh_manager.disconnect()
        self.monitor = self.local_monitor
        self.monitoring_mode = 'local'
        self.connection_label.config(
            text="📍 Monitoring: Local Server",
            foreground='green'
        )
        
        self.cpu_history.clear()
        self.ram_history.clear()
        self.net_upload_history.clear()
        self.net_download_history.clear()
    
    def refresh_resources(self):
        self.resources_text.delete('1.0', 'end')
        
        self.resources_text.insert('end', "=== ADVANCED RESOURCE MONITORING ===\n\n")
        
        gpu_info = self.resource_monitor.get_gpu_info()
        self.resources_text.insert('end', "=== GPU INFORMATION ===\n")
        for gpu in gpu_info:
            self.resources_text.insert('end', f"GPU #{gpu['id']}: {gpu['name']}\n")
            self.resources_text.insert('end', f"  Load: {gpu['load']:.1f}%\n")
            self.resources_text.insert('end', f"  Memory: {gpu['memory_used']:.0f} MB / {gpu['memory_total']:.0f} MB ({gpu['memory_percent']:.1f}%)\n")
            self.resources_text.insert('end', f"  Temperature: {gpu['temperature']:.1f}°C\n\n")
        
        battery_info = self.resource_monitor.get_battery_info()
        self.resources_text.insert('end', "=== BATTERY INFORMATION ===\n")
        if battery_info['present']:
            self.resources_text.insert('end', f"Battery Level: {battery_info['percent']:.1f}%\n")
            self.resources_text.insert('end', f"Power Status: {'Plugged In' if battery_info['power_plugged'] else 'On Battery'}\n")
            self.resources_text.insert('end', f"Time Remaining: {battery_info['time_left']}\n")
            self.resources_text.insert('end', f"Health Status: {battery_info['health']}\n\n")
        else:
            self.resources_text.insert('end', "No battery detected (Desktop system)\n\n")
        
        temps = self.resource_monitor.get_temperature_sensors()
        self.resources_text.insert('end', "=== TEMPERATURE SENSORS ===\n")
        for temp in temps[:10]:
            self.resources_text.insert('end', f"{temp['sensor']} - {temp['label']}: {temp['current']:.1f}°C")
            if temp['high'] > 0:
                self.resources_text.insert('end', f" (High: {temp['high']:.1f}°C, Critical: {temp['critical']:.1f}°C)")
            self.resources_text.insert('end', "\n")
        
        self.resources_text.insert('end', "\n")
    
    def run_security_scan(self):
        self.security_text.delete('1.0', 'end')
        self.security_text.insert('end', "Running security scan...\n\n")
        self.root.update()
        
        results = self.security_manager.run_security_scan()
        
        self.security_text.insert('end', f"=== SECURITY SCAN RESULTS ===\n")
        self.security_text.insert('end', f"Timestamp: {results['timestamp']}\n")
        self.security_text.insert('end', f"Security Score: {results['security_score']}/100\n\n")
        
        if results['security_score'] >= 80:
            self.security_text.insert('end', "✅ EXCELLENT SECURITY\n\n")
        elif results['security_score'] >= 60:
            self.security_text.insert('end', "⚠️ GOOD SECURITY (Some improvements needed)\n\n")
        else:
            self.security_text.insert('end', "❌ POOR SECURITY (Immediate action required)\n\n")
        
        self.security_text.insert('end', "=== WARNINGS ===\n")
        if results['warnings']:
            for warning in results['warnings']:
                self.security_text.insert('end', f"{warning}\n")
        else:
            self.security_text.insert('end', "No warnings detected\n")
        
        self.security_text.insert('end', "\n=== RECOMMENDATIONS ===\n")
        for rec in results['recommendations']:
            self.security_text.insert('end', f"{rec}\n")
        
        self.security_text.insert('end', f"\n=== OPEN PORTS ===\n")
        self.security_text.insert('end', f"Total Open Ports: {results['open_ports']['total']}\n")
        if results['open_ports']['suspicious']:
            self.security_text.insert('end', f"Suspicious Ports: {len(results['open_ports']['suspicious'])}\n")
        
        self.security_text.insert('end', f"\n=== SUSPICIOUS PROCESSES ===\n")
        if results['suspicious_processes']:
            for proc in results['suspicious_processes']:
                self.security_text.insert('end', f"PID {proc['pid']}: {proc['name']} - {proc['reason']}\n")
        else:
            self.security_text.insert('end', "No suspicious processes detected\n")
        
        self.security_text.insert('end', f"\n=== FIREWALL STATUS ===\n")
        self.security_text.insert('end', f"Status: {results['firewall_status']['status']}\n")
        self.security_text.insert('end', f"Details: {results['firewall_status']['details']}\n")
    
    def view_open_ports(self):
        self.security_text.delete('1.0', 'end')
        self.security_text.insert('end', "=== OPEN NETWORK PORTS ===\n\n")
        
        port_info = self.security_manager.scan_open_ports()
        
        self.security_text.insert('end', f"Total Open Ports: {port_info['total']}\n\n")
        
        for port in port_info['ports'][:50]:
            status = "⚠️ SUSPICIOUS" if port['suspicious'] else "✓"
            self.security_text.insert('end', f"{status} Port {port['port']} - {port['process']} (PID: {port['pid']})\n")
        
        if port_info['suspicious']:
            self.security_text.insert('end', f"\n⚠️ WARNING: {len(port_info['suspicious'])} suspicious ports detected!\n")
    
    def check_firewall(self):
        self.security_text.delete('1.0', 'end')
        self.security_text.insert('end', "=== FIREWALL STATUS ===\n\n")
        
        firewall = self.security_manager.check_firewall_status()
        
        self.security_text.insert('end', f"Firewall: {firewall['details']}\n")
        self.security_text.insert('end', f"Status: {firewall['status']}\n")
        self.security_text.insert('end', f"Enabled: {'Yes' if firewall['enabled'] else 'No'}\n\n")
        
        if not firewall['enabled']:
            self.security_text.insert('end', "⚠️ WARNING: Firewall is not enabled!\n")
            self.security_text.insert('end', "Your system is vulnerable to network attacks.\n")
            self.security_text.insert('end', "Please enable your firewall immediately.\n")
        else:
            self.security_text.insert('end', "✅ Firewall is active and protecting your system.\n")
    
    def export_to_pdf(self):
        """Export system overview to PDF"""
        try:
            default_filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Save System Report"
            )
            
            if filename:
                self.pdf_exporter = PDFExporter(
                    self.monitor,
                    self.optimizer,
                    self.device_manager,
                    self.resource_monitor,
                    self.security_manager
                )
                
                self.pdf_exporter.generate_report(filename)
                messagebox.showinfo("Success", f"System report exported successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF:\n{str(e)}")
    
    def on_closing(self):
        self.running = False
        self.ssh_manager.disconnect()
        self.root.destroy()

def main():
    try:
        root = tk.Tk()
        app = SystemMonitorApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        print("GUI initialized. Starting main loop...")
        root.mainloop()
    except tk.TclError as e:
        print(f"Tkinter error: {e}")
        print("GUI cannot start without a display.")
        sys.exit(1)

if __name__ == "__main__":
    main()
