#!/usr/bin/env python3
"""
Simple startup script for the minimal SDN Web GUI
Works with existing Flask installation
"""

import sys
import os

def check_flask():
    """Check if Flask is available"""
    try:
        import flask
        print("✅ Flask found: version {}".format(flask.__version__))
        return True
    except ImportError:
        print("❌ Flask not found. Please install Flask:")
        print("   pip install flask")
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        'minimal_gui.py',
        'simple_switch_13.py',
        'custom5.py',
        'templates/minimal_index.html'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print("   - {}".format(file))
        return False
    
    return True

def main():
    """Main startup function"""
    print("🌐 Minimal SDN Web GUI Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('simple_switch_13.py'):
        print("❌ Please run this script from the basic/ directory")
        return 1
    
    # Check required files
    print("📁 Checking required files...")
    if not check_files():
        return 1
    print("✅ All required files found!")
    
    # Check Flask
    print("📦 Checking Flask...")
    if not check_flask():
        return 1
    
    # Start the minimal web GUI
    print("\n🚀 Starting Minimal SDN Web GUI...")
    print("📍 Access URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Import and run the minimal GUI
        from minimal_gui import app, sdn_manager
        
        # Add startup message
        sdn_manager.log_message("Minimal Web GUI started successfully")
        sdn_manager.log_message("Ready to manage SDN components")
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print("\n❌ Error starting server: {}".format(e))
        print("\nTroubleshooting:")
        print("1. Make sure you're in the basic/ directory")
        print("2. Check that Flask is properly installed")
        print("3. Ensure port 5000 is available")
        return 1

if __name__ == '__main__':
    sys.exit(main())
