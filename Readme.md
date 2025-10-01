# Cross-Platform Server Monitor & Optimizer

## Overview

A Python-based desktop application for real-time system monitoring and optimization across Windows, macOS, and Linux platforms. The application provides comprehensive system metrics visualization, process management, security scanning, and remote server monitoring capabilities via SSH. Built with Tkinter for the GUI and psutil for system metrics, it offers both local and remote monitoring with a focus on cross-platform compatibility.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**GUI Framework: Tkinter with Matplotlib Integration**
- **Decision**: Use Tkinter as the primary GUI framework with embedded matplotlib charts
- **Rationale**: Tkinter is Python's standard GUI library with native cross-platform support, requires no additional dependencies, and integrates well with matplotlib for real-time data visualization
- **Implementation**: Tabbed interface with separate views for Dashboard, Processes, Optimizer, Devices, Resources, Security, and Remote monitoring
- **Visualization**: Uses matplotlib with TkAgg backend and deque collections (maxlen=50) for rolling time-series graphs of CPU, RAM, and network metrics
- **Trade-offs**: Limited modern UI aesthetics compared to web-based solutions, but eliminates browser dependency and provides true desktop integration

**Modular Component Architecture**
- **Decision**: Separate concerns into distinct Python modules for each major feature area
- **Rationale**: Improves maintainability, testability, and allows independent development of features
- **Components**:
  - `SystemMonitor`: Local system metrics collection via psutil
  - `RemoteSystemMonitor`: SSH-based remote metrics collection
  - `SystemOptimizer`: Cleanup and optimization operations
  - `DeviceManager`: Storage device detection and management
  - `ResourceMonitor`: Advanced monitoring (GPU, battery, temperature sensors)
  - `SecurityManager`: Security scanning, port monitoring, intrusion detection
  - `SSHConnectionManager`: Remote connection handling with security features
  - `PDFExporter`: Report generation functionality

### Backend Architecture

**Cross-Platform System Monitoring Strategy**
- **Decision**: Use psutil as the primary system metrics library with OS-specific fallbacks
- **Rationale**: psutil provides unified API across platforms while allowing platform-specific customizations where needed
- **Platform Detection**: Uses `platform.system()` to branch logic for Windows, Darwin (macOS), and Linux-specific features
- **OS-Specific Implementations**:
  - Windows: Uses `ctypes` for drive type detection, WMI for some metrics
  - macOS: Uses `vm_stat` and `ioreg` commands for specific metrics
  - Linux: Uses `/sys/class` filesystem readings and standard Unix tools

**Remote Monitoring via SSH**
- **Decision**: Implement SSH-based command execution for remote monitoring
- **Rationale**: SSH provides secure, universal access to remote systems without requiring agent installation
- **Implementation**: Uses paramiko library for SSH connections with support for both password and key-based authentication
- **Command Strategy**: Executes platform-appropriate commands (top/sar for Linux/Mac, PowerShell for Windows) and parses output
- **Security**: Implements host key verification, connection logging, and secure credential handling

**Security Architecture**
- **Decision**: Built-in security scanning and monitoring without external dependencies
- **Components**:
  - Port scanning using psutil's network connections
  - Process analysis for suspicious activity
  - Firewall status checking via OS-specific commands
  - Failed login attempt tracking
  - Security scoring algorithm
- **Rationale**: Provides immediate security insights without requiring separate security tools or cloud services

**Resource Optimization Strategy**
- **Decision**: Implement safe, reversible optimization operations with user control
- **Operations**:
  - Temporary file cleanup from OS-specific directories
  - Memory release via Python garbage collection and OS-specific commands
  - Zombie/unresponsive process termination
- **Safety**: All operations check permissions and provide detailed logging of actions taken

**Data Persistence and State Management**
- **Decision**: In-memory state management with optional PDF export for reports
- **Rationale**: Desktop application doesn't require persistent database; session data is sufficient
- **Implementation**: Uses Python collections (deque, defaultdict) for time-series and aggregated data
- **Export**: FPDF library for generating portable system reports

## External Dependencies

### Core System Libraries
- **psutil**: Cross-platform system and process utilities - primary metrics collection library
- **paramiko**: SSH2 protocol implementation for remote server connections
- **matplotlib**: Plotting library for real-time graph visualizations with TkAgg backend integration

### Optional/Enhanced Features
- **GPUtil**: GPU monitoring (fallback gracefully if not available)
- **numpy**: Required by matplotlib for numerical operations
- **fpdf**: PDF report generation (FPDF library)

### Standard Library Dependencies
- **tkinter**: Python's standard GUI toolkit (included with Python)
- **platform**: OS detection and platform-specific logic
- **subprocess**: OS command execution for platform-specific operations
- **ctypes**: Windows API access for drive type detection

### Build and Distribution
- **PyInstaller**: Packages application into standalone executables for Windows (.exe), macOS (.app), and Linux (binary)
- **Build Strategy**: Separate spec files for each platform (build_windows.spec, build_macos.spec, build_linux.spec)
- **Dependency Handling**: `dependency_installer.py` module auto-installs missing packages on first run (skipped in frozen executables)

### Platform-Specific Commands and Tools
- **Linux**: Uses `top`, `sar`, `free`, `lsblk`, `udevadm`, `ufw`, `iptables` commands
- **macOS**: Uses `top`, `sar`, `vm_stat`, `ioreg`, `diskutil`, system_profiler commands
- **Windows**: Uses PowerShell commands via subprocess for WMI queries and system information

### Security and Authentication
- **Host Key Verification**: Uses paramiko's host key policies (WarningPolicy) with verification logging
- **Credential Storage**: Supports SSH keys from filesystem or environment variables (designed for Replit secrets integration)
- **Connection Logging**: Tracks all connection attempts and security events in memory