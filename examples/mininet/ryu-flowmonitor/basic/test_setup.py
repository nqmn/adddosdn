#!/usr/bin/env python3
"""
Test script to verify the SDN Web GUI setup
This script performs basic checks without starting the actual services
"""

import os
import sys
import importlib.util

def test_file_exists(filename, description):
    """Test if a file exists"""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ {description}: {filename} - NOT FOUND")
        return False

def test_python_import(module_name, description):
    """Test if a Python module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError:
        print(f"❌ {description}: {module_name} - NOT AVAILABLE")
        return False

def test_file_syntax(filename, description):
    """Test if a Python file has valid syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            compile(f.read(), filename, 'exec')
        print(f"✅ {description}: {filename}")
        return True
    except SyntaxError as e:
        print(f"❌ {description}: {filename} - SYNTAX ERROR: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {description}: {filename} - FILE NOT FOUND")
        return False
    except UnicodeDecodeError as e:
        print(f"⚠️ {description}: {filename} - ENCODING ISSUE: {e}")
        return True  # Don't fail for encoding issues

def main():
    """Main test function"""
    print("🧪 SDN Web GUI Setup Test")
    print("=" * 50)

    all_tests_passed = True

    # Test 1: Check required files
    print("\n📁 Testing File Existence:")
    files_to_test = [
        ('web_gui.py', 'Main web application'),
        ('simple_switch_13.py', 'Ryu controller'),
        ('custom5.py', 'Mininet topology'),
        ('start_gui.py', 'Startup script'),
        ('requirements.txt', 'Dependencies file'),
        ('templates/index.html', 'Web interface template'),
        ('README.md', 'Documentation')
    ]

    for filename, description in files_to_test:
        if not test_file_exists(filename, description):
            all_tests_passed = False

    # Test 2: Check Python syntax
    print("\n🐍 Testing Python File Syntax:")
    python_files = [
        ('web_gui.py', 'Main web application syntax'),
        ('simple_switch_13.py', 'Ryu controller syntax'),
        ('custom5.py', 'Mininet topology syntax'),
        ('start_gui.py', 'Startup script syntax')
    ]

    for filename, description in python_files:
        if not test_file_syntax(filename, description):
            all_tests_passed = False

    # Test 3: Check basic Python modules
    print("\n📦 Testing Basic Python Modules:")
    basic_modules = [
        ('sys', 'System module'),
        ('os', 'Operating system module'),
        ('json', 'JSON module'),
        ('threading', 'Threading module'),
        ('subprocess', 'Subprocess module')
    ]

    for module, description in basic_modules:
        if not test_python_import(module, description):
            all_tests_passed = False

    # Test 4: Check optional dependencies (these might not be installed yet)
    print("\n🔧 Testing Optional Dependencies:")
    optional_modules = [
        ('flask', 'Flask web framework'),
        ('flask_socketio', 'Flask-SocketIO'),
        ('psutil', 'System utilities'),
        ('mininet', 'Mininet framework'),
        ('ryu', 'Ryu controller framework')
    ]

    optional_missing = []
    for module, description in optional_modules:
        if not test_python_import(module, description):
            optional_missing.append(module)

    # Test 5: Check HTML template
    print("\n🌐 Testing HTML Template:")
    if os.path.exists('templates/index.html'):
        try:
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SDN Web GUI' in content and 'socket.io' in content:
                    print("✅ HTML template content: Valid structure")
                else:
                    print("❌ HTML template content: Missing required elements")
                    all_tests_passed = False
        except Exception as e:
            print(f"❌ HTML template content: Error reading file - {e}")
            all_tests_passed = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    if all_tests_passed:
        print("🎉 All core tests PASSED!")
        print("✅ The SDN Web GUI setup appears to be correct.")
    else:
        print("⚠️  Some core tests FAILED!")
        print("❌ Please fix the issues above before running the web GUI.")

    if optional_missing:
        print(f"\n📦 Missing optional dependencies: {', '.join(optional_missing)}")
        print("💡 Install them with: pip install -r requirements.txt")
    else:
        print("\n🎯 All dependencies are available!")

    print("\n🚀 Next steps:")
    if all_tests_passed and not optional_missing:
        print("   1. Run: python start_gui.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Start using the web interface!")
    elif all_tests_passed:
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run: python start_gui.py")
        print("   3. Open: http://localhost:5000")
    else:
        print("   1. Fix the file issues shown above")
        print("   2. Re-run this test script")
        print("   3. Install dependencies when tests pass")

    return 0 if all_tests_passed else 1

if __name__ == '__main__':
    sys.exit(main())
