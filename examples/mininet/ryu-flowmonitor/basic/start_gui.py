#!/usr/bin/env python3
"""
Startup script for the SDN Web GUI
This script checks dependencies and starts the web interface
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_socketio',
        'psutil'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")

        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            return False

    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'web_gui.py',
        'simple_switch_13.py',
        'custom5.py',
        'templates/index.html'
    ]

    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    return True

def main():
    """Main startup function"""
    print("🌐 SDN Web GUI Startup")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('simple_switch_13.py'):
        print("❌ Please run this script from the basic/ directory")
        print("   Current directory should contain simple_switch_13.py and custom5.py")
        return 1

    # Check required files
    print("📁 Checking required files...")
    if not check_files():
        return 1
    print("✅ All required files found!")

    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return 1
    print("✅ All dependencies satisfied!")

    # Start the web GUI
    print("\n🚀 Starting SDN Web GUI...")
    print("📍 Access URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Import and run the web GUI
        from web_gui import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
