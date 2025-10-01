import subprocess
import sys
import importlib.util

def check_and_install_dependencies():
    """
    Check if required dependencies are installed and install them if missing.
    This function runs on first launch to ensure all dependencies are available.
    Skips installation when running as frozen executable (PyInstaller).
    """
    if getattr(sys, 'frozen', False):
        return True
    required_packages = {
        'psutil': 'psutil',
        'matplotlib': 'matplotlib',
        'numpy': 'numpy',
        'paramiko': 'paramiko',
        'GPUtil': 'GPUtil',
        'fpdf': 'fpdf2'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        if importlib.util.find_spec(import_name) is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"Missing packages detected: {', '.join(missing_packages)}")
        print("Installing missing dependencies...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                return False
        
        print("All dependencies installed successfully!")
    
    return True

if __name__ == "__main__":
    check_and_install_dependencies()
