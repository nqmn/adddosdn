#!/usr/bin/env python3
"""
Test script for the simplified controller.
This tests the basic functionality without requiring Ryu to be installed.
"""

import sys
import traceback

def test_simplified_controller_import():
    """Test if the simplified controller can be imported"""
    print("Testing simplified controller import...")
    
    try:
        import simple_controller
        print("✓ simple_controller imported successfully")
        
        # Check if the main class is available
        if hasattr(simple_controller, 'SimpleFlowMonitorController'):
            print("✓ SimpleFlowMonitorController class found")
            
            # Try to create an instance
            try:
                controller = simple_controller.SimpleFlowMonitorController()
                print("✓ SimpleFlowMonitorController instance created successfully")
                print(f"  Controller ID: {controller.controller_id}")
                print(f"  Is Root: {controller.is_root}")
                print(f"  Start Time: {controller.start_time}")
                return controller
            except Exception as e:
                print(f"✗ SimpleFlowMonitorController instantiation failed: {e}")
                traceback.print_exc()
                return None
        else:
            print("✗ SimpleFlowMonitorController class not found")
            return None
            
    except ImportError as e:
        print(f"✗ Simplified controller import failed: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"✗ Simplified controller import error: {e}")
        traceback.print_exc()
        return None

def test_ddos_detector(controller):
    """Test DDoS detector functionality"""
    print("\nTesting DDoS detector...")
    
    try:
        detector = controller.ddos_detector
        print("✓ DDoS detector accessible")
        print(f"  Controller ID: {detector.controller_id}")
        print(f"  Is Root: {detector.is_root}")
        print(f"  Detection Threshold: {detector.detection_threshold}")
        
        # Test feature extraction
        test_flow_stats = {
            'packet_count': 100,
            'byte_count': 150000,
            'duration_sec': 10,
            'priority': 1
        }
        
        features = detector.extract_flow_features(test_flow_stats)
        print(f"✓ Feature extraction successful: {len(features)} features")
        
        # Test DDoS detection
        is_ddos, confidence = detector.detect_ddos(features)
        print(f"✓ DDoS detection test: DDoS={is_ddos}, Confidence={confidence:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ DDoS detector test failed: {e}")
        traceback.print_exc()
        return False

def test_federated_manager(controller):
    """Test federated learning manager"""
    print("\nTesting federated learning manager...")
    
    try:
        manager = controller.federated_manager
        print("✓ Federated manager accessible")
        print(f"  Is Root: {manager.is_root}")
        print(f"  Root Address: {manager.root_address}")
        
        # Test model update (should return None in simplified mode)
        result = manager.send_model_update({'test': 'data'})
        print(f"✓ Model update test: {result}")
        
        return True
    except Exception as e:
        print(f"✗ Federated manager test failed: {e}")
        traceback.print_exc()
        return False

def test_cicflow_integration(controller):
    """Test CICFlowMeter integration"""
    print("\nTesting CICFlowMeter integration...")
    
    try:
        cicflow = controller.cicflow_integration
        print("✓ CICFlowMeter integration accessible")
        
        # Test getting features
        features = cicflow.get_latest_features(5)
        print(f"✓ Feature retrieval test: {len(features)} features")
        
        if features:
            print(f"  Sample feature: {features[0]}")
        
        return True
    except Exception as e:
        print(f"✗ CICFlowMeter integration test failed: {e}")
        traceback.print_exc()
        return False

def test_controller_functionality(controller):
    """Test basic controller functionality"""
    print("\nTesting controller functionality...")
    
    try:
        # Test logging
        controller.log_activity('info', 'Test log message')
        print(f"✓ Logging test: {len(controller.activity_log)} log entries")
        
        # Test status
        status = controller.get_status()
        print(f"✓ Status test: {len(status)} status fields")
        print(f"  Uptime: {status['uptime']} seconds")
        print(f"  RYU Available: {status['ryu_available']}")
        print(f"  ML Available: {status['ml_available']}")
        
        # Test DDoS detection functionality
        controller.test_ddos_detection()
        print("✓ DDoS detection functionality test completed")
        
        return True
    except Exception as e:
        print(f"✗ Controller functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_compatibility_imports():
    """Test compatibility with original controller imports"""
    print("\nTesting compatibility imports...")
    
    try:
        import simple_controller
        
        # Test if compatibility aliases work
        controller_class = simple_controller.FlowMonitorController
        detector_class = simple_controller.DDoSDetector
        federated_class = simple_controller.FederatedLearningManager
        cicflow_class = simple_controller.CICFlowMeterIntegration
        
        print("✓ FlowMonitorController alias works")
        print("✓ DDoSDetector alias works")
        print("✓ FederatedLearningManager alias works")
        print("✓ CICFlowMeterIntegration alias works")
        
        # Test creating instances with aliases
        controller = controller_class()
        print("✓ Controller created using alias")
        
        return True
    except Exception as e:
        print(f"✗ Compatibility imports test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SIMPLIFIED CONTROLLER TEST SUITE")
    print("=" * 60)
    
    all_passed = True
    
    # Test simplified controller import
    controller = test_simplified_controller_import()
    if not controller:
        all_passed = False
        print("\n✗ Cannot proceed with other tests - controller import failed")
        return False
    
    # Test DDoS detector
    if not test_ddos_detector(controller):
        all_passed = False
    
    # Test federated manager
    if not test_federated_manager(controller):
        all_passed = False
    
    # Test CICFlowMeter integration
    if not test_cicflow_integration(controller):
        all_passed = False
    
    # Test controller functionality
    if not test_controller_functionality(controller):
        all_passed = False
    
    # Test compatibility imports
    if not test_compatibility_imports():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("The simplified controller is working correctly!")
        print("\nNext steps:")
        print("1. Install Ryu framework: pip install ryu")
        print("2. Install webob: pip install webob")
        print("3. Test with the original controller")
    else:
        print("✗ SOME TESTS FAILED")
        print("Check the error messages above for details.")
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
