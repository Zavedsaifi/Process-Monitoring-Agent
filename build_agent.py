#!/usr/bin/env python3
"""
Build script for creating the Process Monitor Agent executable.
Uses PyInstaller to create a standalone EXE file.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
    
    try:
        import psutil
        print("✓ psutil is installed")
    except ImportError:
        print("✗ psutil not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        print("✓ psutil installed successfully")
    
    try:
        import requests
        print("✓ requests is installed")
    except ImportError:
        print("✗ requests not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("✓ requests installed successfully")

def create_spec_file():
    """Create a PyInstaller spec file for the agent."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['agent/process_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[('agent/config.py', 'agent')],
    hiddenimports=[
        'psutil',
        'requests',
        'socket',
        'json',
        'time',
        'logging',
        'datetime',
        'typing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ProcessMonitorAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('ProcessMonitorAgent.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    try:
        # Run PyInstaller
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "ProcessMonitorAgent.spec"
        ])
        
        print("✓ Executable built successfully")
        
        # Check if the executable was created
        exe_path = Path("dist/ProcessMonitorAgent.exe")
        if exe_path.exists():
            print(f"✓ Executable created at: {exe_path.absolute()}")
            
            # Copy to root directory for easy access
            shutil.copy2(exe_path, "ProcessMonitorAgent.exe")
            print("✓ Executable copied to root directory")
            
            return True
        else:
            print("✗ Executable not found in dist directory")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed with error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during build: {e}")
        return False

def create_batch_file():
    """Create a batch file for easy execution."""
    batch_content = '''@echo off
echo Starting Process Monitor Agent...
echo.
echo This will collect system process information and send it to the backend.
echo Make sure the Django backend is running at http://localhost:8000
echo.
echo Press Ctrl+C to stop the agent.
echo.
pause

ProcessMonitorAgent.exe
pause
'''
    
    with open('run_agent.bat', 'w') as f:
        f.write(batch_content)
    
    print("✓ Created run_agent.bat file")

def cleanup():
    """Clean up build artifacts."""
    print("Cleaning up build artifacts...")
    
    # Remove spec file
    if os.path.exists('ProcessMonitorAgent.spec'):
        os.remove('ProcessMonitorAgent.spec')
    
    # Remove build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("✓ Cleanup completed")

def main():
    """Main build process."""
    print("=" * 50)
    print("Process Monitor Agent - Build Script")
    print("=" * 50)
    print()
    
    try:
        # Check dependencies
        print("Checking dependencies...")
        check_dependencies()
        print()
        
        # Create spec file
        print("Creating PyInstaller configuration...")
        create_spec_file()
        print()
        
        # Build executable
        print("Building executable...")
        if build_executable():
            print()
            
            # Create batch file
            print("Creating helper files...")
            create_batch_file()
            print()
            
            print("=" * 50)
            print("BUILD COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print()
            print("Files created:")
            print("  - ProcessMonitorAgent.exe (main executable)")
            print("  - run_agent.bat (easy execution script)")
            print()
            print("To run the agent:")
            print("  1. Double-click ProcessMonitorAgent.exe, or")
            print("  2. Double-click run_agent.bat")
            print()
            print("Note: Make sure the Django backend is running first!")
            print()
            
        else:
            print("✗ Build failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n✗ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        print("Cleaning up...")
        cleanup()

if __name__ == "__main__":
    main() 