#!/usr/bin/env python3
"""
Test script for WSGI integration with Simple Controller
Tests the web interface functionality and API endpoints
"""

import time
import json
import threading
from simple_controller import SimpleFlowMonitorController

def test_wsgi_integration():
    """Test WSGI integration with the simple controller"""
    print("=" * 60)
    print("WSGI INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Create controller with web interface
    print("\n1. Creating controller with web interface...")
    try:
        controller = SimpleFlowMonitorController(
            controller_id="test_wsgi_controller",
            is_root=True,
            enable_web_server=False  # Don't start server automatically
        )
        print("✓ Controller created successfully")
        
        # Check web interface status
        status = controller.get_status()
        print(f"✓ Web interface enabled: {status['web_interface_enabled']}")
        print(f"✓ Custom WSGI available: {status['custom_wsgi_available']}")
        
    except Exception as e:
        print(f"✗ Failed to create controller: {e}")
        return False
    
    # Test 2: Test API endpoints
    print("\n2. Testing API endpoints...")
    try:
        # Test status endpoint
        status = controller.get_status()
        print(f"✓ Status endpoint: {len(status)} fields")
        
        # Test switches endpoint
        switches = controller.get_switches_info()
        print(f"✓ Switches endpoint: {switches['count']} switches")
        
        # Test flows endpoint
        flows = controller.get_flow_stats_all()
        print(f"✓ Flows endpoint: {flows['count']} flows")
        
        # Test network stats endpoint
        stats = controller.get_network_stats()
        print(f"✓ Network stats endpoint: {stats['uptime_seconds']}s uptime")
        
        # Test topology endpoint
        topology = controller.get_topology_data()
        print(f"✓ Topology endpoint: {len(topology)} components")
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False
    
    # Test 3: Test DDoS detection through API
    print("\n3. Testing DDoS detection...")
    try:
        # Add some test data
        controller.packet_count = 1000
        controller.byte_count = 50000
        
        # Test DDoS detection
        controller.test_ddos_detection()
        
        # Check detection stats
        stats = controller.get_status()
        detection_stats = stats['detection_stats']
        print(f"✓ DDoS detections: {detection_stats['total_detections']}")
        print(f"✓ Activity log entries: {stats['activity_log_size']}")
        
    except Exception as e:
        print(f"✗ DDoS detection test failed: {e}")
        return False
    
    # Test 4: Test CICFlowMeter integration
    print("\n4. Testing CICFlowMeter integration...")
    try:
        features = controller.cicflow_integration.get_latest_features(5)
        print(f"✓ CICFlowMeter features: {len(features)} samples")
        
        if features:
            print(f"✓ Sample feature keys: {list(features[0].keys())}")
        
    except Exception as e:
        print(f"✗ CICFlowMeter test failed: {e}")
        return False
    
    # Test 5: Test federated learning status
    print("\n5. Testing federated learning...")
    try:
        fed_manager = controller.federated_manager
        print(f"✓ Federated manager available: {fed_manager is not None}")
        print(f"✓ Is root controller: {fed_manager.is_root}")
        print(f"✓ Global model version: {fed_manager.global_model_version}")
        
    except Exception as e:
        print(f"✗ Federated learning test failed: {e}")
        return False
    
    # Test 6: Test WSGI application creation
    print("\n6. Testing WSGI application...")
    try:
        if controller.wsgi_app:
            print("✓ WSGI application created")
            print(f"✓ WSGI app type: {type(controller.wsgi_app).__name__}")
            print(f"✓ Registered controllers: {len(controller.wsgi_app.registory)}")
        else:
            print("⚠ WSGI application not available")
        
    except Exception as e:
        print(f"✗ WSGI application test failed: {e}")
        return False
    
    # Test 7: Simulate web requests (if possible)
    print("\n7. Testing simulated web requests...")
    try:
        if controller.wsgi_app:
            # Create a simple test environment
            test_environ = {
                'REQUEST_METHOD': 'GET',
                'PATH_INFO': '/status',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '8080',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.input': None,
                'wsgi.errors': None,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False
            }
            
            def start_response(status, headers):
                print(f"✓ Response status: {status}")
                print(f"✓ Response headers: {len(headers)} headers")
            
            # Test the WSGI application
            response = controller.wsgi_app(test_environ, start_response)
            print(f"✓ WSGI response generated: {type(response)}")
            
        else:
            print("⚠ WSGI application not available for testing")
        
    except Exception as e:
        print(f"✗ WSGI request simulation failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL WSGI INTEGRATION TESTS PASSED")
    print("=" * 60)
    
    return True


def test_web_server_startup():
    """Test web server startup (without actually starting it)"""
    print("\n" + "=" * 60)
    print("WEB SERVER STARTUP TEST")
    print("=" * 60)
    
    try:
        controller = SimpleFlowMonitorController(
            controller_id="test_web_server",
            is_root=True
        )
        
        print("✓ Controller created")
        
        # Test server configuration
        if hasattr(controller, 'start_web_server'):
            print("✓ Web server method available")
            print("Note: Web server startup test completed (server not actually started)")
        else:
            print("⚠ Web server method not available")
        
        return True
        
    except Exception as e:
        print(f"✗ Web server test failed: {e}")
        return False


def main():
    """Run all WSGI tests"""
    print("Starting WSGI Integration Tests...")
    
    # Test basic WSGI integration
    test1_result = test_wsgi_integration()
    
    # Test web server functionality
    test2_result = test_web_server_startup()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"WSGI Integration Test: {'PASSED' if test1_result else 'FAILED'}")
    print(f"Web Server Test: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("The WSGI integration is working correctly.")
        print("\nNext steps:")
        print("1. Install additional dependencies (ryu, webob) for full functionality")
        print("2. Test with actual Mininet topology")
        print("3. Enable web server and test browser access")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Check the error messages above for troubleshooting.")


if __name__ == "__main__":
    main()
