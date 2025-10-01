# Server Monitor & Optimizer - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation & Setup](#installation--setup)
4. [User Guide](#user-guide)
5. [PDF Export Feature](#pdf-export-feature)
6. [Technical Architecture](#technical-architecture)
7. [Module Documentation](#module-documentation)
8. [Remote Monitoring](#remote-monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Development & Building](#development--building)

---

## Overview

Server Monitor & Optimizer is a cross-platform desktop application built with Python and Tkinter. It provides comprehensive system monitoring, optimization tools, and remote server management capabilities.

### Key Highlights
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Real-Time Monitoring**: Live graphs and statistics
- **Remote Capabilities**: Monitor remote servers via SSH
- **System Optimization**: Clean temp files, free memory, manage processes
- **Security Scanning**: Port scanning, firewall checks, intrusion detection
- **PDF Export**: Generate comprehensive system reports

---

## Features

### 1. Dashboard
- Real-time CPU usage monitoring with historical graphs
- RAM usage tracking with detailed memory statistics
- Network activity monitoring (upload/download speeds)
- Disk usage visualization
- Live updating charts using matplotlib

### 2. Process Management
- View all running processes with detailed information
- Sort processes by PID, name, CPU%, memory%, or status
- Kill/terminate selected processes
- Monitor top resource-consuming processes

### 3. System Optimization
- **Clear Temp Files**: Remove temporary files from system directories
- **Free Memory**: Release unused RAM and clear system cache
- **Kill Unresponsive Processes**: Terminate zombie and stopped processes
- **Quick Optimize**: Run all optimization tasks at once

### 4. Device Management
- Detect connected storage devices (USB drives, external drives)
- Display device information (size, usage, filesystem type)
- Identify removable devices
- Safe eject/unmount for Linux and macOS

### 5. Advanced Resources
- **GPU Monitoring**: Load, memory usage, and temperature
- **Battery Information**: Level, power status, time remaining, health
- **Temperature Sensors**: Monitor CPU and system temperatures

### 6. Security
- **Port Scanning**: Detect open network ports and identify suspicious ones
- **Firewall Status**: Check firewall configuration
- **Security Score**: Comprehensive security assessment
- **Intrusion Detection**: Identify suspicious processes

### 7. System Information
- Operating system details
- Processor information
- Memory and disk statistics
- System uptime and boot time

### 8. Remote Monitoring
- Connect to remote servers via SSH
- Support for password and SSH key authentication
- Monitor remote Linux, Windows (PowerShell), and macOS systems
- Secure credential management

### 9. PDF Export
- Generate comprehensive system reports
- Include all monitoring data in a single PDF
- Automatic timestamping
- Professional formatting

---

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Desktop environment (GUI required)

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd Sensei/ServerSensei
```

### Step 2: Install Dependencies
The application includes automatic dependency installation. Simply run:

```bash
python main.py
```

Dependencies will be automatically installed on first run:
- `psutil` - System and process monitoring
- `matplotlib` - Real-time graphs
- `paramiko` - SSH connections
- `GPUtil` - GPU monitoring
- `fpdf2` - PDF generation

### Step 3: Run the Application
```bash
python main.py
```

---

## User Guide

### Starting the Application

1. Launch the application:
   ```bash
   python main.py
   ```

2. The main window will open with multiple tabs:
   - Dashboard
   - Processes
   - Optimize
   - Devices
   - Resources
   - Security
   - System Info

### Using the Dashboard

The Dashboard tab provides real-time monitoring:

- **Current Stats**: View CPU, RAM, disk usage, and network activity
- **Graphs**: Four real-time charts showing:
  - CPU usage history
  - RAM usage history
  - Network upload speeds
  - Network download speeds

### Managing Processes

1. Navigate to the **Processes** tab
2. Click **Refresh Processes** to update the list
3. Select a process to view details
4. Click **Kill Selected Process** to terminate a process

### System Optimization

1. Go to the **Optimize** tab
2. Choose from optimization tools:
   - **Clear Temp Files**: Remove temporary files
   - **Free Memory**: Release unused RAM
   - **Kill Unresponsive Processes**: Terminate stuck processes
   - **Quick Optimize**: Run all optimizations

3. View results in the output window

### Device Management

1. Open the **Devices** tab
2. View all connected storage devices
3. Select a removable device
4. Click **Eject Selected Device** to safely unmount (Linux/macOS)

### Resource Monitoring

1. Navigate to **Resources** tab
2. Click **Refresh Resource Data** to update
3. View:
   - GPU information (load, memory, temperature)
   - Battery status (if applicable)
   - Temperature sensors

### Security Scanning

1. Go to the **Security** tab
2. Click **Run Security Scan** for comprehensive analysis
3. View:
   - Security score
   - Open ports
   - Firewall status
   - Suspicious processes
   - Recommendations

### System Information

1. Open the **System Info** tab
2. View detailed system information:
   - OS and architecture
   - Processor details
   - Memory statistics
   - Disk information

---

## PDF Export Feature

### Overview
The PDF export feature generates a comprehensive system report containing all monitoring data in a professional PDF format.

### How to Use

1. **Via Menu**: Click **File → Export to PDF**
2. **Save Dialog**: Choose where to save the PDF
3. **Default Name**: `system_report_YYYYMMDD_HHMMSS.pdf`
4. **Confirmation**: Success message with file location

### Report Contents

The generated PDF includes:

1. **System Information**
   - OS details, architecture, processor
   - Hostname, CPU cores, uptime

2. **CPU & Memory Usage**
   - Current CPU usage
   - Per-core CPU statistics
   - Memory usage breakdown

3. **Disk Information**
   - All mounted drives
   - Storage capacity and usage
   - File system types

4. **Network Activity**
   - Upload/download speeds
   - Total data transferred

5. **Top Processes**
   - Top 20 processes by CPU usage
   - Process details (PID, name, CPU%, memory%, status)

6. **Connected Devices**
   - Storage devices
   - Removable media
   - Usage statistics

7. **Advanced Resources**
   - GPU information
   - Battery status
   - Temperature sensors

8. **Security Overview**
   - Security score
   - Open ports
   - Firewall status
   - Warnings and recommendations

### PDF Format
- Professional layout with headers and footers
- Page numbers
- Timestamp of report generation
- Color-coded sections
- Monospace font for process listings

---

## Technical Architecture

### Application Structure

```
main.py                   - Main GUI application and entry point
system_monitor.py         - Local system monitoring (psutil)
remote_monitor.py         - Remote system monitoring via SSH
ssh_manager.py           - SSH connection management
connection_dialog.py     - Connection settings GUI dialog
optimizer.py             - System optimization tools
device_manager.py        - Device detection and management
resource_monitor.py      - GPU, battery, temperature monitoring
security_manager.py      - Security scanning and analysis
pdf_exporter.py          - PDF report generation
dependency_installer.py  - Automatic dependency installation
```

### Technology Stack

- **GUI Framework**: Tkinter (built-in with Python)
- **System Monitoring**: psutil
- **Graphs**: matplotlib with TkAgg backend
- **SSH**: paramiko
- **PDF Generation**: fpdf2
- **GPU Monitoring**: GPUtil

### Design Patterns

1. **Separation of Concerns**: Each module handles specific functionality
2. **Cross-Platform Compatibility**: OS detection and platform-specific code
3. **Error Handling**: Graceful degradation and user-friendly error messages
4. **Modular Architecture**: Easy to extend and maintain

### Data Flow

```
User Interaction (GUI)
         ↓
   SystemMonitorApp
         ↓
   ├── SystemMonitor (local)
   ├── RemoteMonitor (SSH)
   ├── Optimizer
   ├── DeviceManager
   ├── ResourceMonitor
   ├── SecurityManager
   └── PDFExporter
         ↓
   Display/Export Results
```

---

## Module Documentation

### system_monitor.py

**Purpose**: Local system monitoring using psutil

**Key Methods**:
- `get_cpu_usage()` - Current CPU usage percentage
- `get_cpu_per_core()` - Per-core CPU usage
- `get_memory_info()` - RAM usage statistics
- `get_disk_usage()` - Disk usage for all partitions
- `get_network_activity()` - Network upload/download speeds
- `get_processes()` - List of running processes
- `kill_process(pid)` - Terminate a process
- `get_system_info()` - System information

### remote_monitor.py

**Purpose**: Remote system monitoring via SSH

**Key Methods**:
- `get_cpu_usage()` - Remote CPU usage
- `get_memory_info()` - Remote memory statistics
- `get_disk_usage()` - Remote disk usage
- `get_network_activity()` - Remote network activity
- `get_processes()` - Remote process list
- `get_system_info()` - Remote system information

**Supported Systems**: Linux, macOS, Windows (PowerShell)

### ssh_manager.py

**Purpose**: SSH connection management

**Key Methods**:
- `connect_with_password(host, port, username, password)` - Password auth
- `connect_with_key(host, port, username, key_data/key_file)` - SSH key auth
- `execute_command(command)` - Execute remote command
- `disconnect()` - Close SSH connection
- `is_remote()` - Check if connected

**Security Features**:
- Host key verification
- Connection logging
- Secure credential handling

### optimizer.py

**Purpose**: System optimization tools

**Key Methods**:
- `clear_temp_files()` - Remove temporary files
- `free_memory()` - Release unused RAM
- `kill_unresponsive_processes()` - Terminate zombie/stopped processes
- `quick_optimize()` - Run all optimizations
- `get_optimization_summary(results)` - Format optimization results

**Platform Support**: Windows, macOS, Linux

### device_manager.py

**Purpose**: Device detection and management

**Key Methods**:
- `get_connected_devices()` - List storage devices
- `eject_device(mountpoint)` - Safely eject device
- `get_usb_devices_info()` - USB device details

**Removable Device Detection**: Windows (Drive Type), Linux (sysfs), macOS (Volumes)

### resource_monitor.py

**Purpose**: Advanced resource monitoring

**Key Methods**:
- `get_gpu_info()` - GPU load, memory, temperature
- `get_battery_info()` - Battery level, status, health
- `get_temperature_sensors()` - CPU and system temperatures

**GPU Support**: NVIDIA (via GPUtil), fallback methods for other systems

### security_manager.py

**Purpose**: Security scanning and analysis

**Key Methods**:
- `run_security_scan()` - Comprehensive security check
- `scan_open_ports()` - Network port scanning
- `detect_suspicious_processes()` - Intrusion detection
- `check_firewall_status()` - Firewall configuration check

**Security Score Calculation**: Based on open ports, firewall status, and suspicious processes

### pdf_exporter.py

**Purpose**: PDF report generation

**Key Classes**:
- `SystemReportPDF(FPDF)` - Custom PDF class with header/footer
- `PDFExporter` - Report generation logic

**Key Methods**:
- `generate_report(filename)` - Create complete PDF report

**Report Sections**: System info, CPU/memory, disk, network, processes, devices, resources, security

### connection_dialog.py

**Purpose**: SSH connection settings GUI

**Features**:
- Server type selection (local/remote)
- Authentication method (password/SSH key)
- SSH key from secret or file
- Input validation

---

## Remote Monitoring

### Connecting to Remote Servers

1. Click **Connection → Connection Settings** (or **Change Connection** button)
2. Select **Remote Server (SSH)**
3. Enter connection details:
   - Host (IP address or hostname)
   - Port (default: 22)
   - Username

### Authentication Methods

#### Password Authentication
1. Select **Password** authentication
2. Enter password
3. Click **Connect**

#### SSH Key Authentication
1. Select **SSH Key** authentication
2. Choose key source:
   - **From Secret**: Uses `SSH_PRIVATE_KEY` environment variable
   - **From File**: Browse to select private key file
3. Click **Connect**

### Setting Up SSH Keys in Replit

If using Replit Secrets:
1. Create a secret named `SSH_PRIVATE_KEY`
2. Paste your private key content
3. Select "From Secret" in connection dialog

### Disconnecting

- Click **Connection → Disconnect**
- Or switch back to **Local Server** in connection dialog

### Remote Monitoring Features

All monitoring features work on remote servers:
- Dashboard with real-time stats
- Process management
- System information
- Resource monitoring (if available)
- Security scanning

---

## Troubleshooting

### Application Won't Start

**Issue**: No GUI window appears

**Solutions**:
1. Check if display is available:
   ```bash
   echo $DISPLAY
   ```
2. For remote systems, enable X11 forwarding:
   ```bash
   ssh -X user@host
   ```
3. Use VNC or remote desktop for headless systems

### Import Errors

**Issue**: "ModuleNotFoundError" for dependencies

**Solution**:
- Dependencies auto-install on first run
- Manual installation:
  ```bash
  pip install psutil matplotlib paramiko GPUtil fpdf2
  ```

### SSH Connection Fails

**Issue**: Cannot connect to remote server

**Solutions**:
1. Verify SSH service is running on remote server:
   ```bash
   sudo systemctl status sshd
   ```
2. Check firewall allows SSH (port 22)
3. Verify credentials are correct
4. For key authentication, ensure key permissions:
   ```bash
   chmod 600 ~/.ssh/id_rsa
   ```

### GPU Information Not Available

**Issue**: "No GPU detected" message

**Solutions**:
1. Install GPU drivers (NVIDIA, AMD, Intel)
2. For NVIDIA: Install nvidia-smi utility
3. GPUtil may not support all GPU types

### Permission Errors

**Issue**: "Permission denied" for optimization tasks

**Solutions**:
1. Run with elevated privileges:
   - Linux/macOS: `sudo python main.py`
   - Windows: Run as Administrator
2. Some operations require root/admin access:
   - Clearing system temp files
   - Killing system processes
   - Ejecting devices

### PDF Export Fails

**Issue**: Error when generating PDF

**Solutions**:
1. Check disk space for output file
2. Ensure write permissions for save location
3. Verify fpdf2 is installed:
   ```bash
   pip install fpdf2
   ```

### High CPU Usage

**Issue**: Application uses too much CPU

**Solutions**:
1. Increase monitoring interval (currently 2 seconds)
2. Reduce graph history length
3. Disable unnecessary monitoring tabs

---

## Development & Building

### Development Setup

1. Clone repository
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run in development mode:
   ```bash
   python main.py
   ```

### Building Executables

#### Using PyInstaller

**Windows**:
```bash
pyinstaller --onefile --windowed --name="ServerMonitor" main.py
```

**macOS**:
```bash
pyinstaller --onefile --windowed --name="ServerMonitor" main.py
```

**Linux**:
```bash
pyinstaller --onefile --name="ServerMonitor" main.py
```

#### Build Specifications

Pre-configured spec files are available:
- `build_windows.spec` - Windows executable
- `build_macos.spec` - macOS application bundle
- `build_linux.spec` - Linux binary

Build with spec file:
```bash
pyinstaller build_windows.spec
```

### Project Structure

```
SERVER/ServerSensei/
├── main.py                    # Main application
├── system_monitor.py          # System monitoring
├── remote_monitor.py          # Remote monitoring
├── ssh_manager.py            # SSH management
├── connection_dialog.py      # Connection dialog
├── optimizer.py              # Optimization tools
├── device_manager.py         # Device management
├── resource_monitor.py       # Resource monitoring
├── security_manager.py       # Security scanning
├── pdf_exporter.py           # PDF generation
├── dependency_installer.py   # Dependency management
├── DOCUMENTATION.md          # This file
├── BUILD_INSTRUCTIONS.txt    # Build guide
└── pyproject.toml           # Project configuration
```

### Adding New Features

1. Create new module in `SERVER/ServerSensei/`
2. Import in `main.py`
3. Initialize in `__init__` method
4. Add UI components in appropriate tab
5. Update documentation

### Testing

Manual testing checklist:
- [ ] Dashboard updates in real-time
- [ ] Process management works
- [ ] Optimization tools function
- [ ] Device detection works
- [ ] GPU/battery/temperature monitoring (if available)
- [ ] Security scanning completes
- [ ] SSH connection works
- [ ] PDF export generates report
- [ ] Cross-platform compatibility

---

## FAQ

**Q: Does this work on Raspberry Pi?**
A: Yes, as long as you have a desktop environment installed.

**Q: Can I monitor multiple servers simultaneously?**
A: Currently, only one remote connection at a time. Switch between servers via Connection Settings.

**Q: Is the SSH connection secure?**
A: Yes, uses industry-standard paramiko library with host key verification and secure credential handling.

**Q: Can I customize the PDF report?**
A: Yes, edit `pdf_exporter.py` to modify sections, formatting, or add custom content.

**Q: Does it support Docker containers?**
A: Monitor the host system. For containers, use container-specific tools.

**Q: How accurate is the security score?**
A: It's a basic assessment based on open ports, firewall status, and process analysis. For comprehensive security audits, use specialized tools.

---

## License & Credits

This application uses the following open-source libraries:
- psutil (BSD-3-Clause)
- matplotlib (PSF License)
- paramiko (LGPL)
- GPUtil (MIT)
- fpdf2 (LGPL)

---

## Support

For issues, questions, or contributions:
1. Check this documentation
2. Review troubleshooting section
3. Check project repository for updates

---

**Version**: 2.0
**Last Updated**: September 30, 2025
**Author**: Server Monitor Team
