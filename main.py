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
import json

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
        self.comparison_tab = ttk.Frame(notebook)
        self.sysinfo_tab = ttk.Frame(notebook)
        
        notebook.add(self.dashboard_tab, text='Dashboard')
        notebook.add(self.processes_tab, text='Processes')
        notebook.add(self.optimize_tab, text='Optimize')
        notebook.add(self.devices_tab, text='Devices')
        notebook.add(self.resources_tab, text='Resources')
        notebook.add(self.security_tab, text='Security')
        notebook.add(self.comparison_tab, text='Comparison')
        notebook.add(self.sysinfo_tab, text='System Info')
        
        self.create_dashboard_tab()
        self.create_processes_tab()
        self.create_optimize_tab()
        self.create_devices_tab()
        self.create_resources_tab()
        self.create_security_tab()
        self.create_comparison_tab()
        self.create_sysinfo_tab()

    def create_comparison_tab(self):
        """Create the comparison tab with charts and summary"""
        main_frame = ttk.Frame(self.comparison_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Button frame at the top
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="📊 Load Comparison Data", command=self.load_comparison_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Comparison", command=self.clear_comparison).pack(side='left', padx=5)
        
        # Create main content area with two sections
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Left side - Charts
        chart_container = ttk.Frame(content_frame)
        chart_container.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        chart_frame = ttk.LabelFrame(chart_container, text="📈 Comparison Charts", padding=10)
        chart_frame.pack(fill='both', expand=True)
        
        self.comparison_fig = Figure(figsize=(8, 8))
        
        # Create 6 subplots for comparison
        self.comp_ax1 = self.comparison_fig.add_subplot(231)  # CPU
        self.comp_ax2 = self.comparison_fig.add_subplot(232)  # Memory
        self.comp_ax3 = self.comparison_fig.add_subplot(233)  # Disk
        self.comp_ax4 = self.comparison_fig.add_subplot(234)  # Network Upload
        self.comp_ax5 = self.comparison_fig.add_subplot(235)  # Network Download
        self.comp_ax6 = self.comparison_fig.add_subplot(236)  # Battery
        
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, chart_frame)
        self.comparison_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.comparison_fig.tight_layout(pad=2.0)
        
        # Initialize with placeholder
        for ax in [self.comp_ax1, self.comp_ax2, self.comp_ax3, self.comp_ax4, self.comp_ax5, self.comp_ax6]:
            ax.text(0.5, 0.5, 'No Data\nLoad Comparison', 
                   ha='center', va='center', fontsize=10, color='gray')
            ax.set_xticks([])
            ax.set_yticks([])
        self.comparison_fig.tight_layout(pad=2.0)
        self.comparison_canvas.draw()
        
        # Right side - Summary Text
        summary_container = ttk.Frame(content_frame)
        summary_container.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        summary_frame = ttk.LabelFrame(summary_container, text="📋 Detailed Analysis & Recommendations", padding=10)
        summary_frame.pack(fill='both', expand=True)
        
        self.comparison_text = scrolledtext.ScrolledText(
            summary_frame, 
            height=35, 
            width=70,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.comparison_text.pack(fill='both', expand=True)
        
        # Initial message
        self.comparison_text.insert('end', "=" * 70 + "\n")
        self.comparison_text.insert('end', "SYSTEM COMPARISON SUMMARY\n")
        self.comparison_text.insert('end', "=" * 70 + "\n\n")
        self.comparison_text.insert('end', "Click 'Load Comparison Data' to compare the current\n")
        self.comparison_text.insert('end', "system state with the previous snapshot.\n\n")
        self.comparison_text.insert('end', "This will display:\n")
        self.comparison_text.insert('end', "  • Visual charts showing changes\n")
        self.comparison_text.insert('end', "  • Detailed metrics (CPU, Memory, Disk, etc.)\n")
        self.comparison_text.insert('end', "  • Identified issues and warnings\n")
        self.comparison_text.insert('end', "  • Actionable recommendations\n")
        self.comparison_text.insert('end', "  • Positive improvements\n\n")
        self.comparison_text.insert('end', "=" * 70 + "\n")
    
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
    
    def load_comparison_data(self):
        """Load and display comparison data between current and previous snapshot"""
        try:
            # Update status in summary
            self.comparison_text.delete('1.0', 'end')
            self.comparison_text.insert('end', "⏳ Loading comparison data...\n\n")
            self.comparison_text.update_idletasks()

            # Get snapshots
            current_snapshot = self.pdf_exporter._get_snapshot()
            previous_snapshot = self.pdf_exporter._load_previous_snapshot()

            if not previous_snapshot:
                self.comparison_text.insert('end', "📌 No previous snapshot found.\n\n")
                self.comparison_text.insert('end', "A snapshot has been saved for future comparisons.\n\n")
                self.comparison_text.insert('end', "Please wait a few minutes and click\n")
                self.comparison_text.insert('end', "'Load Comparison Data' again to see the\n")
                self.comparison_text.insert('end', "comparison between snapshots.\n")
                self.pdf_exporter._save_snapshot(current_snapshot)
                return

            # Compute differences
            self.comparison_text.insert('end', "🔄 Computing differences...\n")
            self.comparison_text.update_idletasks()
            
            diffs = self.pdf_exporter._compare_snapshots(previous_snapshot, current_snapshot)

            if not diffs:
                self.comparison_text.insert('end', "⚠️  Warning: No comparison data generated.\n")
                return

            # Draw charts
            self.comparison_text.insert('end', "📊 Generating comparison charts...\n")
            self.comparison_text.update_idletasks()
            self.display_comparison_charts(previous_snapshot, current_snapshot, diffs)

            # Clear and display summaries
            self.comparison_text.delete('1.0', 'end')
            self.display_comparison_summary(previous_snapshot, current_snapshot, diffs)
            self.display_overall_summary(diffs)

            # Save current snapshot for next comparison
            self.pdf_exporter._save_snapshot(current_snapshot)

            messagebox.showinfo("Success", 
                              "✅ Comparison data loaded successfully!\n\n" +
                              "Check the charts and summary for detailed analysis.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load comparison data:\n{e}")

    def display_comparison_summary(self, previous_snapshot, current_snapshot, diffs):
        """Display detailed comparison summary in the Text widget"""
        try:
            # Helper to format increase/decrease
            def delta_status(old, new):
                diff = new - old
                status = "INCREASED ⬆️" if diff > 0 else "DECREASED ⬇️" if diff < 0 else "UNCHANGED ➡️"
                return diff, status

            # --- Header ---
            self.comparison_text.insert('end', "=" * 70 + "\n")
            self.comparison_text.insert('end', "SYSTEM COMPARISON SUMMARY\n")
            self.comparison_text.insert('end', "=" * 70 + "\n\n")
            self.comparison_text.update_idletasks()

            # --- Timestamps ---
            try:
                old_time = datetime.fromisoformat(previous_snapshot.get('timestamp'))
                new_time = datetime.fromisoformat(current_snapshot.get('timestamp'))
                delta = new_time - old_time
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60

                self.comparison_text.insert('end', f"📅 Previous: {old_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.comparison_text.insert('end', f"📅 Current:  {new_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.comparison_text.insert('end', f"⏱️  Duration: {days}d {hours}h {minutes}m\n\n")
                self.comparison_text.update_idletasks()
            except Exception as e:
                self.comparison_text.insert('end', f"Could not parse timestamps: {e}\n\n")

            # --- CPU ---
            if 'cpu' in diffs:
                try:
                    old_cpu = diffs['cpu']['old']
                    new_cpu = diffs['cpu']['new']
                    diff, status = delta_status(old_cpu, new_cpu)
                    
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', "🖥️  CPU USAGE\n")
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', f"Previous: {old_cpu:.1f}%\n")
                    self.comparison_text.insert('end', f"Current:  {new_cpu:.1f}%\n")
                    self.comparison_text.insert('end', f"Change:   {diff:+.1f}% ({status})\n")
                    
                    if new_cpu >= 80:
                        self.comparison_text.insert('end', "⚠️  WARNING: High CPU usage detected!\n")
                    self.comparison_text.insert('end', "\n")
                    self.comparison_text.update_idletasks()
                except Exception as e:
                    self.comparison_text.insert('end', f"Error displaying CPU: {e}\n\n")

            # --- Memory ---
            if 'memory' in diffs:
                try:
                    old_mem = diffs['memory']['old']
                    new_mem = diffs['memory']['new']
                    delta_gb = new_mem['used_gb'] - old_mem['used_gb']
                    delta_pct = new_mem['percent'] - old_mem['percent']
                    
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', "💾 MEMORY USAGE\n")
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', f"Total:    {new_mem['total_gb']:.2f} GB\n")
                    self.comparison_text.insert('end', f"Previous: {old_mem['used_gb']:.2f} GB ({old_mem['percent']:.1f}%)\n")
                    self.comparison_text.insert('end', f"Current:  {new_mem['used_gb']:.2f} GB ({new_mem['percent']:.1f}%)\n")
                    self.comparison_text.insert('end', f"Change:   {delta_gb:+.2f} GB ({delta_pct:+.1f}%)\n")
                    
                    if new_mem['percent'] >= 85:
                        self.comparison_text.insert('end', "⚠️  WARNING: High memory usage detected!\n")
                    self.comparison_text.insert('end', "\n")
                    self.comparison_text.update_idletasks()
                except Exception as e:
                    self.comparison_text.insert('end', f"Error displaying memory: {e}\n\n")

            # --- Disk ---
            if 'disk' in diffs:
                try:
                    old_disks = {d['mountpoint']: d for d in diffs['disk']['old']}
                    new_disks = {d['mountpoint']: d for d in diffs['disk']['new']}
                    
                    for mount, new_disk in new_disks.items():
                        old_disk = old_disks.get(mount)
                        if not old_disk:
                            continue
                            
                        delta_gb = new_disk['used_gb'] - old_disk['used_gb']
                        delta_pct = new_disk['percent'] - old_disk['percent']
                        
                        self.comparison_text.insert('end', "─" * 70 + "\n")
                        self.comparison_text.insert('end', f"💿 DISK: {mount}\n")
                        self.comparison_text.insert('end', "─" * 70 + "\n")
                        self.comparison_text.insert('end', f"Previous: {old_disk['used_gb']:.2f} GB ({old_disk['percent']:.1f}%)\n")
                        self.comparison_text.insert('end', f"Current:  {new_disk['used_gb']:.2f} GB ({new_disk['percent']:.1f}%)\n")
                        self.comparison_text.insert('end', f"Change:   {delta_gb:+.2f} GB ({delta_pct:+.1f}%)\n")
                        
                        if new_disk['percent'] >= 85:
                            self.comparison_text.insert('end', f"⚠️  WARNING: Low disk space on {mount}!\n")
                        self.comparison_text.insert('end', "\n")
                    self.comparison_text.update_idletasks()
                except Exception as e:
                    self.comparison_text.insert('end', f"Error displaying disk: {e}\n\n")

            # --- Network ---
            if 'network' in diffs:
                try:
                    old_net = diffs['network']['old']
                    new_net = diffs['network']['new']
                    
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', "🌐 NETWORK ACTIVITY\n")
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', f"Upload:\n")
                    self.comparison_text.insert('end', f"  Previous: {old_net['upload_speed']/1024:.2f} KB/s\n")
                    self.comparison_text.insert('end', f"  Current:  {new_net['upload_speed']/1024:.2f} KB/s\n")
                    self.comparison_text.insert('end', f"Download:\n")
                    self.comparison_text.insert('end', f"  Previous: {old_net['download_speed']/1024:.2f} KB/s\n")
                    self.comparison_text.insert('end', f"  Current:  {new_net['download_speed']/1024:.2f} KB/s\n")
                    self.comparison_text.insert('end', "\n")
                    self.comparison_text.update_idletasks()
                except Exception as e:
                    self.comparison_text.insert('end', f"Error displaying network: {e}\n\n")

            # --- Battery ---
            if 'battery' in diffs:
                try:
                    old_bat = diffs['battery']['old']
                    new_bat = diffs['battery']['new']
                    delta_pct = new_bat['percent'] - old_bat['percent']
                    
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', "🔋 BATTERY STATUS\n")
                    self.comparison_text.insert('end', "─" * 70 + "\n")
                    self.comparison_text.insert('end', f"Previous: {old_bat['percent']:.1f}%\n")
                    self.comparison_text.insert('end', f"Current:  {new_bat['percent']:.1f}%\n")
                    self.comparison_text.insert('end', f"Change:   {delta_pct:+.1f}%\n")
                    
                    if new_bat['percent'] < 20:
                        self.comparison_text.insert('end', "⚠️  WARNING: Low battery level!\n")
                    self.comparison_text.insert('end', "\n")
                    self.comparison_text.update_idletasks()
                except Exception as e:
                    self.comparison_text.insert('end', f"Error displaying battery: {e}\n\n")

            self.comparison_text.see('end')
            
        except Exception as e:
            import traceback
            self.comparison_text.insert('end', f"\n❌ ERROR in display_comparison_summary:\n{str(e)}\n")
            self.comparison_text.insert('end', f"{traceback.format_exc()}\n")

    def display_overall_summary(self, diffs):
        """Display overall summary with issues and recommendations"""
        try:
            self.comparison_text.insert('end', "\n" + "=" * 70 + "\n")
            self.comparison_text.insert('end', "📊 OVERALL SUMMARY & RECOMMENDATIONS\n")
            self.comparison_text.insert('end', "=" * 70 + "\n\n")
            self.comparison_text.update_idletasks()

            issues = []
            recommendations = []
            positives = []

            # --- CPU Analysis ---
            if 'cpu' in diffs:
                try:
                    old_cpu = diffs['cpu']['old']
                    new_cpu = diffs['cpu']['new']
                    delta = new_cpu - old_cpu
                    
                    if abs(delta) > 10:
                        if delta > 0:
                            issues.append(f"CPU usage increased by {delta:.1f}%")
                            recommendations.append("Monitor CPU-intensive processes in Processes tab")
                        else:
                            positives.append(f"CPU usage decreased by {abs(delta):.1f}%")
                    
                    if new_cpu > 80:
                        issues.append(f"CPU usage is high ({new_cpu:.1f}%)")
                        recommendations.append("Close unnecessary applications")
                        recommendations.append("Check for runaway processes")
                except Exception as e:
                    pass

            # --- Memory Analysis ---
            if 'memory' in diffs:
                try:
                    old_mem = diffs['memory']['old']
                    new_mem = diffs['memory']['new']
                    delta_pct = new_mem['percent'] - old_mem['percent']
                    
                    if abs(delta_pct) > 10:
                        if delta_pct > 0:
                            issues.append(f"Memory usage increased by {delta_pct:.1f}%")
                            recommendations.append("Check for memory leaks")
                            recommendations.append("Review resource-heavy processes")
                        else:
                            positives.append(f"Memory usage decreased by {abs(delta_pct):.1f}%")
                    
                    if new_mem['percent'] > 85:
                        issues.append(f"Memory usage is critical ({new_mem['percent']:.1f}%)")
                        recommendations.append("Close applications immediately")
                        recommendations.append("Consider upgrading RAM")
                except Exception as e:
                    pass

            # --- Disk Analysis ---
            if 'disk' in diffs:
                try:
                    old_disks_list = diffs['disk']['old']
                    new_disks_list = diffs['disk']['new']
                    
                    for i, new_disk in enumerate(new_disks_list):
                        if i < len(old_disks_list):
                            old_disk = old_disks_list[i]
                            delta_gb = new_disk['used_gb'] - old_disk['used_gb']
                            mount = new_disk['mountpoint']
                            
                            if delta_gb > 5:
                                issues.append(f"Disk {mount} increased by {delta_gb:.2f} GB")
                                recommendations.append(f"Clean up {mount} using Optimize tab")
                            
                            if new_disk['percent'] > 85:
                                issues.append(f"Disk {mount} low on space ({new_disk['percent']:.1f}%)")
                                recommendations.append(f"Free up space on {mount} immediately")
                except Exception as e:
                    pass

            # --- Display Results ---
            if positives:
                self.comparison_text.insert('end', "✅ POSITIVE CHANGES:\n")
                for p in positives:
                    self.comparison_text.insert('end', f"  • {p}\n")
                self.comparison_text.insert('end', "\n")
                self.comparison_text.update_idletasks()

            if issues:
                self.comparison_text.insert('end', "⚠️  ISSUES DETECTED:\n")
                for issue in issues:
                    self.comparison_text.insert('end', f"  • {issue}\n")
                self.comparison_text.insert('end', "\n")
                self.comparison_text.update_idletasks()
            else:
                self.comparison_text.insert('end', "✅ NO CRITICAL ISSUES DETECTED\n\n")
                self.comparison_text.update_idletasks()

            if recommendations:
                self.comparison_text.insert('end', "💡 RECOMMENDATIONS:\n")
                # Remove duplicates
                seen = set()
                unique_recs = []
                for rec in recommendations:
                    if rec not in seen:
                        seen.add(rec)
                        unique_recs.append(rec)
                
                for rec in unique_recs:
                    self.comparison_text.insert('end', f"  • {rec}\n")
                self.comparison_text.insert('end', "\n")
                self.comparison_text.update_idletasks()
            else:
                self.comparison_text.insert('end', "✅ System operating normally\n\n")
                self.comparison_text.update_idletasks()

            self.comparison_text.insert('end', "=" * 70 + "\n")
            self.comparison_text.see('end')
            self.comparison_text.update_idletasks()
            
        except Exception as e:
            import traceback
            self.comparison_text.insert('end', f"\n❌ ERROR in display_overall_summary:\n{str(e)}\n")

    
    def display_comparison_charts(self, old_snap, new_snap, diffs):
        """Display comparison charts for CPU, Memory, Disk, Network, and Battery"""
    
        # Clear all axes
        for ax in [self.comp_ax1, self.comp_ax2, self.comp_ax3, self.comp_ax4, self.comp_ax5, self.comp_ax6]:
            ax.clear()
    
        # --- CPU ---
        if 'cpu' in diffs:
            old_cpu = diffs['cpu']['old']
            new_cpu = diffs['cpu']['new']
            color = ['#3498db', '#2ecc71' if new_cpu < old_cpu else '#e74c3c']
            self.comp_ax1.bar(['Previous', 'Current'], [old_cpu, new_cpu], color=color)
            self.comp_ax1.set_title('CPU Usage (%)')
            self.comp_ax1.set_ylim(0, 100)
            self.comp_ax1.axhline(y=80, color='r', linestyle='--', alpha=0.5, label='High Usage')
            self.comp_ax1.legend()
            delta = new_cpu - old_cpu
            self.comp_ax1.text(0.5, max(old_cpu, new_cpu) + 5, f"{delta:+.1f}%", ha='center', fontsize=10, fontweight='bold')
    
        # --- Memory ---
        if 'memory' in diffs:
            old_mem = diffs['memory']['old']['percent']
            new_mem = diffs['memory']['new']['percent']
            color = ['#3498db', '#2ecc71' if new_mem < old_mem else '#e74c3c']
            self.comp_ax2.bar(['Previous', 'Current'], [old_mem, new_mem], color=color)
            self.comp_ax2.set_title('Memory Usage (%)')
            self.comp_ax2.set_ylim(0, 100)
            self.comp_ax2.axhline(y=85, color='r', linestyle='--', alpha=0.5, label='High Usage')
            self.comp_ax2.legend()
            delta = new_mem - old_mem
            self.comp_ax2.text(0.5, max(old_mem, new_mem) + 5, f"{delta:+.1f}%", ha='center', fontsize=10, fontweight='bold')
    
        # --- Disk (first disk only) ---
        if 'disk' in diffs and len(diffs['disk']['old']) > 0:
            old_disk = diffs['disk']['old'][0]['percent']
            new_disk = diffs['disk']['new'][0]['percent']
            color = ['#3498db', '#2ecc71' if new_disk < old_disk else '#e74c3c']
            self.comp_ax3.bar(['Previous', 'Current'], [old_disk, new_disk], color=color)
            self.comp_ax3.set_title('Disk Usage (%)')
            self.comp_ax3.set_ylim(0, 100)
            self.comp_ax3.axhline(y=85, color='r', linestyle='--', alpha=0.5, label='High Usage')
            self.comp_ax3.legend()
            delta = new_disk - old_disk
            self.comp_ax3.text(0.5, max(old_disk, new_disk) + 5, f"{delta:+.1f}%", ha='center', fontsize=10, fontweight='bold')
    
        # --- Network Upload ---
        if 'network' in diffs:
            old_up = diffs['network']['old']['upload_speed'] / 1024  # KB/s
            new_up = diffs['network']['new']['upload_speed'] / 1024
            color = ['#3498db', '#2ecc71' if new_up > old_up else '#e74c3c']
            self.comp_ax4.bar(['Previous', 'Current'], [old_up, new_up], color=color)
            self.comp_ax4.set_title('Upload Speed (KB/s)')
            max_val = max(old_up, new_up)
            self.comp_ax4.set_ylim(0, max_val * 1.5 if max_val > 0 else 1)
            delta = new_up - old_up
            self.comp_ax4.text(0.5, max_val + max_val * 0.1 if max_val > 0 else 1, f"{delta:+.1f}", ha='center', fontsize=10, fontweight='bold')
    
        # --- Network Download ---
        if 'network' in diffs:
            old_down = diffs['network']['old']['download_speed'] / 1024
            new_down = diffs['network']['new']['download_speed'] / 1024
            color = ['#3498db', '#2ecc71' if new_down > old_down else '#e74c3c']
            self.comp_ax5.bar(['Previous', 'Current'], [old_down, new_down], color=color)
            self.comp_ax5.set_title('Download Speed (KB/s)')
            max_val = max(old_down, new_down)
            self.comp_ax5.set_ylim(0, max_val * 1.5 if max_val > 0 else 1)
            delta = new_down - old_down
            self.comp_ax5.text(0.5, max_val + max_val * 0.1 if max_val > 0 else 1, f"{delta:+.1f}", ha='center', fontsize=10, fontweight='bold')
    
        # --- Battery ---
        if 'battery' in diffs and diffs['battery']['old'] is not None:
            old_bat = diffs['battery']['old']['percent']
            new_bat = diffs['battery']['new']['percent']
            color = ['#3498db', '#2ecc71' if new_bat > old_bat else '#e74c3c']
            self.comp_ax6.bar(['Previous', 'Current'], [old_bat, new_bat], color=color)
            self.comp_ax6.set_title('Battery Level (%)')
            self.comp_ax6.set_ylim(0, 100)
            self.comp_ax6.axhline(y=20, color='r', linestyle='--', alpha=0.5, label='Low Battery')
            self.comp_ax6.legend()
            delta = new_bat - old_bat
            self.comp_ax6.text(0.5, max(old_bat, new_bat) + 5, f"{delta:+.1f}%", ha='center', fontsize=10, fontweight='bold')
    
        # Adjust layout and redraw
        self.comparison_fig.tight_layout(pad=3.0)
        self.comparison_canvas.draw()


    
    def clear_comparison(self):
        """Clear comparison display"""
        # Clear charts
        for ax in [self.comp_ax1, self.comp_ax2, self.comp_ax3, self.comp_ax4, self.comp_ax5, self.comp_ax6]:
            ax.clear()
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14, color='gray')
        
        self.comparison_fig.tight_layout(pad=3.0)
        self.comparison_canvas.draw()
        
        # Clear text
        self.comparison_text.delete('1.0', 'end')
        self.comparison_text.insert('end', "Comparison data cleared.\n")
        self.comparison_text.insert('end', "Click 'Load Comparison Data' to generate a new comparison.\n")
    
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
