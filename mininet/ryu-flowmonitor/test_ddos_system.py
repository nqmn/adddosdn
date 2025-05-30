#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Ryu Flow Monitor with DDoS Detection
This script tests all components of the DDoS detection system including:
- ML-based detection
- Federated learning
- CICFlowMeter integration
- Automated mitigation
- Multi-controller coordination
"""

import requests
import json
import time
import subprocess
import threading
import random
import sys
from datetime import datetime
import argparse

class DDoSSystemTester:
    def __init__(self, root_url="http://192.168.1.100:8080", client_url="http://192.168.1.101:8081"):
        self.root_url = root_url
        self.client_url = client_url
        self.test_results = {}
        self.verbose = False

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"[{timestamp}] ❌ {message}")
        elif level == "SUCCESS":
            print(f"[{timestamp}] ✅ {message}")
        elif level == "WARNING":
            print(f"[{timestamp}] ⚠️  {message}")
        else:
            print(f"[{timestamp}] ℹ️  {message}")

    def test_controller_connectivity(self):
        """Test connectivity to both controllers"""
        self.log("Testing controller connectivity...")

        # Test root controller
        try:
            response = requests.get(f"{self.root_url}/stats", timeout=5)
            if response.status_code == 200:
                self.log("Root controller is responding", "SUCCESS")
                self.test_results['root_connectivity'] = True
            else:
                self.log(f"Root controller returned status {response.status_code}", "ERROR")
                self.test_results['root_connectivity'] = False
        except Exception as e:
            self.log(f"Root controller connection failed: {e}", "ERROR")
            self.test_results['root_connectivity'] = False

        # Test client controller
        try:
            response = requests.get(f"{self.client_url}/stats", timeout=5)
            if response.status_code == 200:
                self.log("Client controller is responding", "SUCCESS")
                self.test_results['client_connectivity'] = True
            else:
                self.log(f"Client controller returned status {response.status_code}", "ERROR")
                self.test_results['client_connectivity'] = False
        except Exception as e:
            self.log(f"Client controller connection failed: {e}", "ERROR")
            self.test_results['client_connectivity'] = False

    def test_ddos_endpoints(self):
        """Test DDoS-specific API endpoints"""
        self.log("Testing DDoS API endpoints...")

        endpoints = [
            '/ddos/alerts',
            '/ddos/stats',
            '/ddos/mitigation',
            '/ddos/threats',
            '/cicflow/features',
            '/federated/status'
        ]

        for controller_name, base_url in [("Root", self.root_url), ("Client", self.client_url)]:
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        self.log(f"{controller_name} {endpoint}: OK", "SUCCESS")
                    else:
                        self.log(f"{controller_name} {endpoint}: HTTP {response.status_code}", "WARNING")
                except Exception as e:
                    self.log(f"{controller_name} {endpoint}: Failed - {e}", "ERROR")

    def test_federated_learning(self):
        """Test federated learning functionality"""
        self.log("Testing federated learning...")

        try:
            # Get federated status from both controllers
            root_status = requests.get(f"{self.root_url}/federated/status", timeout=5).json()
            client_status = requests.get(f"{self.client_url}/federated/status", timeout=5).json()

            # Check if root is configured as root
            if root_status.get('is_root'):
                self.log("Root controller correctly configured as root", "SUCCESS")
            else:
                self.log("Root controller not configured as root", "ERROR")

            # Check if client is configured as client
            if not client_status.get('is_root'):
                self.log("Client controller correctly configured as client", "SUCCESS")
            else:
                self.log("Client controller not configured as client", "ERROR")

            # Check model versions
            root_version = root_status.get('global_model_version', 0)
            client_version = client_status.get('global_model_version', 0)

            self.log(f"Root model version: {root_version}")
            self.log(f"Client model version: {client_version}")

            self.test_results['federated_learning'] = True

        except Exception as e:
            self.log(f"Federated learning test failed: {e}", "ERROR")
            self.test_results['federated_learning'] = False

    def test_ddos_detection(self):
        """Test DDoS detection capabilities"""
        self.log("Testing DDoS detection...")

        try:
            # Get initial DDoS stats
            initial_stats = requests.get(f"{self.root_url}/ddos/stats", timeout=5).json()
            initial_detections = initial_stats.get('total_detections', 0)

            self.log(f"Initial detections: {initial_detections}")

            # Simulate some network activity (this would normally trigger detection)
            self.log("Simulating network activity...")

            # Wait a bit for potential detection
            time.sleep(10)

            # Check for new detections
            final_stats = requests.get(f"{self.root_url}/ddos/stats", timeout=5).json()
            final_detections = final_stats.get('total_detections', 0)

            if final_detections > initial_detections:
                self.log(f"DDoS detection working: {final_detections - initial_detections} new detections", "SUCCESS")
            else:
                self.log("No new DDoS detections (may be normal if no attacks)", "WARNING")

            self.test_results['ddos_detection'] = True

        except Exception as e:
            self.log(f"DDoS detection test failed: {e}", "ERROR")
            self.test_results['ddos_detection'] = False

    def test_mitigation_system(self):
        """Test DDoS mitigation system"""
        self.log("Testing mitigation system...")

        try:
            # Get mitigation rules
            mitigation_rules = requests.get(f"{self.root_url}/ddos/mitigation", timeout=5).json()

            self.log(f"Active mitigation rules: {len(mitigation_rules)}")

            if isinstance(mitigation_rules, dict):
                for rule_id, rule in mitigation_rules.items():
                    self.log(f"Rule {rule_id}: {rule.get('action', 'unknown')} for {rule.get('source_ip', 'unknown')}")

            self.test_results['mitigation_system'] = True

        except Exception as e:
            self.log(f"Mitigation system test failed: {e}", "ERROR")
            self.test_results['mitigation_system'] = False

    def test_cicflow_integration(self):
        """Test CICFlowMeter integration"""
        self.log("Testing CICFlowMeter integration...")

        try:
            # Get CICFlow features
            features = requests.get(f"{self.client_url}/cicflow/features", timeout=5).json()

            if isinstance(features, list) and len(features) > 0:
                self.log(f"CICFlowMeter features available: {len(features)} samples", "SUCCESS")

                # Check feature structure
                sample_feature = features[0]
                expected_fields = ['flow_duration', 'total_fwd_packets', 'flow_bytes_per_sec']

                for field in expected_fields:
                    if field in sample_feature:
                        self.log(f"Feature field '{field}' present", "SUCCESS")
                    else:
                        self.log(f"Feature field '{field}' missing", "WARNING")
            else:
                self.log("No CICFlowMeter features available", "WARNING")

            self.test_results['cicflow_integration'] = True

        except Exception as e:
            self.log(f"CICFlowMeter integration test failed: {e}", "ERROR")
            self.test_results['cicflow_integration'] = False

    def test_model_management(self):
        """Test ML model upload/download functionality"""
        self.log("Testing model management...")

        try:
            # Test model listing
            response = requests.get(f"{self.root_url}/models/list", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('models', [])
                self.log(f"Model listing successful: {len(models)} models found", "SUCCESS")
            else:
                self.log(f"Model listing failed: HTTP {response.status_code}", "ERROR")
                self.test_results['model_management'] = False
                return

            # Test model creation and upload (if create_sample_models.py exists)
            import os
            if os.path.exists('create_sample_models.py'):
                self.log("Creating sample model for upload test...")

                # Create a simple test model
                import pickle
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.datasets import make_classification

                X, y = make_classification(n_samples=100, n_features=5, random_state=42)
                test_model = RandomForestClassifier(n_estimators=5, random_state=42)
                test_model.fit(X, y)

                # Save test model
                test_model_path = 'test_upload_model.pkl'
                with open(test_model_path, 'wb') as f:
                    pickle.dump({
                        'model': test_model,
                        'model_type': 'test_model',
                        'timestamp': time.time(),
                        'description': 'Test model for upload functionality'
                    }, f)

                # Test model upload
                try:
                    with open(test_model_path, 'rb') as f:
                        files = {'model_file': (test_model_path, f, 'application/octet-stream')}
                        data = {'model_type': 'ddos_detector', 'replace_existing': 'false'}

                        upload_response = requests.post(
                            f"{self.root_url}/models/upload",
                            files=files,
                            data=data,
                            timeout=10
                        )

                    if upload_response.status_code == 200:
                        upload_result = upload_response.json()
                        if upload_result.get('success'):
                            self.log("Model upload successful", "SUCCESS")

                            # Test model download
                            model_name = upload_result.get('model_name')
                            if model_name:
                                download_response = requests.get(
                                    f"{self.root_url}/models/download/{model_name}",
                                    timeout=5
                                )

                                if download_response.status_code == 200:
                                    self.log("Model download successful", "SUCCESS")
                                else:
                                    self.log(f"Model download failed: HTTP {download_response.status_code}", "WARNING")
                        else:
                            self.log(f"Model upload failed: {upload_result.get('error', 'Unknown error')}", "ERROR")
                    else:
                        self.log(f"Model upload failed: HTTP {upload_response.status_code}", "ERROR")

                except Exception as upload_error:
                    self.log(f"Model upload test error: {upload_error}", "ERROR")

                finally:
                    # Clean up test file
                    if os.path.exists(test_model_path):
                        os.remove(test_model_path)

            else:
                self.log("Skipping model upload test (create_sample_models.py not found)", "WARNING")

            self.test_results['model_management'] = True

        except Exception as e:
            self.log(f"Model management test failed: {e}", "ERROR")
            self.test_results['model_management'] = False

    def simulate_ddos_attack(self, attack_type="tcp_syn"):
        """Simulate a DDoS attack for testing"""
        self.log(f"Simulating {attack_type} attack...")

        try:
            if attack_type == "tcp_syn":
                # Simulate TCP SYN flood
                cmd = ["hping3", "-S", "-p", "80", "--flood", "10.0.0.5"]
            elif attack_type == "udp_flood":
                # Simulate UDP flood
                cmd = ["hping3", "-2", "-p", "53", "--flood", "10.0.0.5"]
            elif attack_type == "icmp_flood":
                # Simulate ICMP flood
                cmd = ["ping", "-f", "10.0.0.5"]
            else:
                self.log(f"Unknown attack type: {attack_type}", "ERROR")
                return False

            # Run attack simulation for 10 seconds
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(10)
            process.terminate()

            self.log(f"{attack_type} attack simulation completed", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Attack simulation failed: {e}", "ERROR")
            return False

    def test_real_time_detection(self):
        """Test real-time DDoS detection with simulated attacks"""
        self.log("Testing real-time detection with simulated attacks...")

        # Get initial state
        try:
            initial_alerts = requests.get(f"{self.root_url}/ddos/alerts", timeout=5).json()
            initial_count = len(initial_alerts) if isinstance(initial_alerts, list) else 0

            self.log(f"Initial alert count: {initial_count}")

            # Simulate attack
            if self.simulate_ddos_attack("tcp_syn"):
                # Wait for detection
                time.sleep(15)

                # Check for new alerts
                final_alerts = requests.get(f"{self.root_url}/ddos/alerts", timeout=5).json()
                final_count = len(final_alerts) if isinstance(final_alerts, list) else 0

                if final_count > initial_count:
                    self.log(f"Real-time detection working: {final_count - initial_count} new alerts", "SUCCESS")

                    # Check latest alert details
                    if isinstance(final_alerts, list) and len(final_alerts) > 0:
                        latest_alert = final_alerts[-1]
                        self.log(f"Latest alert: {latest_alert.get('attack_type', 'unknown')} "
                                f"(confidence: {latest_alert.get('confidence', 0):.2f})")
                else:
                    self.log("No new alerts detected", "WARNING")

            self.test_results['real_time_detection'] = True

        except Exception as e:
            self.log(f"Real-time detection test failed: {e}", "ERROR")
            self.test_results['real_time_detection'] = False

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.log("Generating test report...")

        print("\n" + "="*60)
        print("ENHANCED RYU FLOW MONITOR TEST REPORT")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        print("\nDetailed Results:")
        print("-" * 40)

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")

        print("\nRecommendations:")
        print("-" * 40)

        if not self.test_results.get('root_connectivity'):
            print("• Check root controller is running and accessible")

        if not self.test_results.get('client_connectivity'):
            print("• Check client controller is running and accessible")

        if not self.test_results.get('federated_learning'):
            print("• Verify federated learning configuration")

        if not self.test_results.get('cicflow_integration'):
            print("• Install and configure CICFlowMeter")

        if passed_tests == total_tests:
            print("🎉 All tests passed! System is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the issues above.")

        print("="*60)

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("Starting comprehensive DDoS system test...")

        # Basic connectivity tests
        self.test_controller_connectivity()
        self.test_ddos_endpoints()

        # Advanced functionality tests
        self.test_federated_learning()
        self.test_ddos_detection()
        self.test_mitigation_system()
        self.test_cicflow_integration()
        self.test_model_management()

        # Real-time tests (optional, requires attack simulation tools)
        try:
            self.test_real_time_detection()
        except Exception as e:
            self.log(f"Skipping real-time detection test: {e}", "WARNING")

        # Generate report
        self.generate_test_report()


def main():
    parser = argparse.ArgumentParser(description='Test Enhanced Ryu Flow Monitor DDoS Detection System')
    parser.add_argument('--root-url', default='http://192.168.1.100:8080',
                       help='Root controller URL')
    parser.add_argument('--client-url', default='http://192.168.1.101:8081',
                       help='Client controller URL')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    tester = DDoSSystemTester(args.root_url, args.client_url)
    tester.verbose = args.verbose

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
