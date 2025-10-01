# Cross-Platform Server Monitor & Optimizer

## Overview

A Python-based desktop application for monitoring and optimizing system resources across Windows, macOS, and Linux platforms. The application provides real-time system monitoring with graphical visualizations, process management, system optimization tools, remote server monitoring via SSH, **advanced resource monitoring (GPU, battery, temperature sensors)**, and **comprehensive security scanning**. Built with Tkinter for the GUI and psutil for system monitoring, it's designed to be packaged as standalone executables using PyInstaller.

## Recent Changes

**Date: September 30, 2025**
- Added advanced resource monitoring: GPU load/temperature, battery health, temperature sensors
- Implemented comprehensive security management: port scanning, intrusion detection, firewall checking
- Enhanced SSH security with host key verification and connection logging
- Added new GUI tabs: Resources and Security
- Improved cross-platform compatibility for monitoring features

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**GUI Framework: Tkinter**
- **Decision**: Use Tkinter as the primary GUI framework
- **Rationale**: Native Python library with cross-platform support, suitable for desktop system monitoring tools, lightweight and doesn't require additional dependencies
- **Components**:
  - Main application window with tabbed interface
  - Real-time graph visualizations using matplotlib with TkAgg backend
  - Scrolled text widgets for logs and process listings
  - Custom dialog windows for SSH connection configuration

**Visualization Layer**
- **Decision**: Integrate matplotlib for real-time data visualization
- **Rationale**: Mature charting library with excellent Tkinter integration, supports live updating graphs
- **Implementation**: Uses deque collections (maxlen=50) to maintain rolling history for CPU, RAM, and network metrics

### Backend Architecture

**Modular Component Design**
The application follows a modular architecture with separation of concerns:

1. **SystemMonitor** (`system_monitor.py`): Local system metrics using psutil, includes temperature monitoring
2. **RemoteSystemMonitor** (`remote_monitor.py`): Remote metrics via SSH command execution
3. **SystemOptimizer** (`optimizer.py`): System cleanup and optimization operations
4. **DeviceManager** (`device_manager.py`): Storage device detection and management
5. **ResourceMonitor** (`resource_monitor.py`): Advanced monitoring (GPU load/memory/temp, battery health, temperature sensors)
6. **SecurityManager** (`security_manager.py`): Security scanning, port monitoring, intrusion detection, firewall checking
7. **SSHConnectionManager** (`ssh_manager.py`): Remote SSH connection handling with host key verification and security logging

**Cross-Platform Compatibility Strategy**
- **Decision**: Use platform detection with OS-specific code paths
- **Rationale**: Different operating systems require different commands and APIs for system operations
- **Implementation**: Each manager class checks `platform.system()` and branches logic accordingly (Windows/Darwin/Linux)

**Remote Monitoring Architecture**
- **Decision**: SSH-based remote monitoring with fallback command strategies
- **Rationale**: SSH is universally available on servers, allows secure remote access without installing agents
- **Implementation**: 
  - Executes platform-appropriate commands over SSH (Linux shell, macOS vm_stat, Windows PowerShell)
  - Falls back through multiple command variants to ensure compatibility
  - Parses command output to extract metrics

### Data Flow and State Management

**Monitoring Data Pipeline**
1. Application switches between local (`SystemMonitor`) and remote (`RemoteSystemMonitor`) monitoring based on connection state
2. Metrics are collected at regular intervals via update loops
3. Historical data stored in fixed-size deques for graph rendering
4. Real-time updates pushed to GUI components

**Connection State Management**
- **SSHConnectionManager** maintains connection state and credentials
- Connection type stored as 'local' or 'remote'
- Main application switches active monitor based on connection type
- Connection logs track authentication attempts and security events

### Security Architecture

**SSH Authentication**
- **Decision**: Support both password and SSH key authentication
- **Rationale**: Flexibility for different server configurations and security policies
- **Security Features**:
  - Host key verification with warning policy
  - Connection event logging
  - Secure credential handling (no plaintext storage in code)
  - Support for SSH keys from Replit secrets or file system

**Security Monitoring Features**
- Port scanning with known malicious port detection
- Suspicious process detection based on behavior patterns
- Firewall status checking (OS-specific)
- Security scoring and recommendation engine
- Failed login attempt tracking

### System Optimization Strategy

**Cleanup Operations**
- **Decision**: OS-specific temporary file cleanup with safety checks
- **Rationale**: Each OS has different temp directories and safe cleanup practices
- **Approach**:
  - Windows: %TEMP%, %TMP%, %LOCALAPPDATA%\Temp
  - macOS: /private/tmp, ~/Library/Caches
  - Linux: /tmp, ~/.cache
  - Safety: Only delete files, not directories; handle permission errors gracefully

**Memory Optimization**
- Python garbage collection triggering
- Process termination for unresponsive/zombie processes
- Cache clearing mechanisms (OS-dependent)

### Dependency Management

**Runtime Dependency Installer**
- **Decision**: Auto-install missing dependencies on first launch
- **Rationale**: Simplifies user setup, ensures all required packages are available
- **Implementation**: `dependency_installer.py` checks for psutil, matplotlib, numpy, paramiko, GPUtil and installs via pip if missing
- **PyInstaller Handling**: Skips installation check when running as frozen executable

## External Dependencies

### Core Python Libraries
- **psutil**: Cross-platform system and process monitoring (CPU, memory, disk, network, processes)
- **tkinter**: Built-in GUI framework (standard library)
- **paramiko**: SSH client for remote server connections
- **matplotlib**: Data visualization and real-time graphing
- **numpy**: Numerical operations (matplotlib dependency)

### Optional/Advanced Monitoring
- **GPUtil**: GPU monitoring for NVIDIA GPUs (optional, graceful degradation if unavailable)

### Build and Distribution
- **PyInstaller**: Packaging application into standalone executables for Windows (.exe), macOS (.app), and Linux (binary)
- Build specifications provided for each platform (`build_windows.spec`, `build_macos.spec`, `build_linux.spec`)

### Platform-Specific Integrations
- **Windows**: ctypes for drive type detection, WMI for system information
- **macOS**: vm_stat and system_profiler commands via subprocess
- **Linux**: Various CLI tools (free, top, sar, lsblk) via subprocess

### Authentication and Storage
- No external database required (stateless monitoring)
- SSH credentials handled in-memory only
- Connection logs stored in memory during session
- Optional SSH key file loading from filesystem