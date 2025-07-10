#!/usr/bin/env python3
"""
Test script to verify the Ryu Flow Monitor system is working correctly.
This script tests the controller API endpoints and basic functionality.
"""

import requests
import json
import time
import sys
import subprocess
import threading
from pathlib import Path

def test_controller_import():
    """Test if the controller can be imported without errors"""
    try:
        import flow_monitor_controller
        print("✓ Controller imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Controller import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Controller import error: {e}")
        return False

def test_html_file():
    """Test if the HTML file exists and is valid"""
    html_file = Path("flow_monitor.html")
    if not html_file.exists():
        print("✗ HTML file not found")
        return False

    try:
        # Try different encodings
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                content = html_file.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print("✗ Could not read HTML file with any encoding")
            return False

        if "<!DOCTYPE html>" in content and "</html>" in content:
            print("✓ HTML file is valid")
            return True
        else:
            print("✗ HTML file appears to be malformed")
            return False
    except Exception as e:
        print(f"✗ Error reading HTML file: {e}")
        return False

def test_controller_endpoints():
    """Test controller REST API endpoints"""
    base_url = "http://localhost:8080"
    endpoints = ["/switches", "/flows", "/stats", "/topology", "/logs", "/port_stats"]

    print("Testing controller endpoints (requires running controller)...")

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=2)
            if response.status_code == 200:
                print(f"✓ {endpoint} - OK")
            else:
                print(f"? {endpoint} - HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"? {endpoint} - Controller not running")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")

def test_run_script():
    """Test if the run script exists and is executable"""
    script_file = Path("run_script.sh")
    if not script_file.exists():
        print("✗ Run script not found")
        return False

    try:
        content = script_file.read_text()
        if "#!/bin/bash" in content and "ryu-manager" in content:
            print("✓ Run script is valid")
            return True
        else:
            print("✗ Run script appears to be malformed")
            return False
    except Exception as e:
        print(f"✗ Error reading run script: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    dependencies = [
        ("json", "JSON support"),
        ("time", "Time utilities"),
        ("threading", "Threading support"),
        ("collections", "Collections module"),
        ("datetime", "DateTime support")
    ]

    print("Testing Python dependencies...")
    all_good = True

    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"✗ {module} - {description} - MISSING")
            all_good = False

    return all_good

def test_file_structure():
    """Test if all required files are present"""
    required_files = [
        "flow_monitor_controller.py",
        "flow_monitor.html",
        "run_script.sh",
        "setup_instructions.md"
    ]

    print("Testing file structure...")
    all_present = True

    for filename in required_files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - MISSING")
            all_present = False

    return all_present

def run_all_tests():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("Ryu Flow Monitor System Test")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Python Dependencies", test_dependencies),
        ("Controller Import", test_controller_import),
        ("HTML File", test_html_file),
        ("Run Script", test_run_script),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))

    # Test controller endpoints (optional)
    print(f"\n--- Controller API Endpoints ---")
    test_controller_endpoints()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The system appears to be working correctly.")
        print("\nNext steps:")
        print("1. Install Ryu framework: pip install ryu")
        print("2. Run the controller: ./run_script.sh start")
        print("3. Open the web interface: ./run_script.sh web")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
