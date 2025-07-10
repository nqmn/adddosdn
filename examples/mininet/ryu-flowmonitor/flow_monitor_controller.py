#!/usr/bin/env python3
"""
Enhanced Ryu Controller Application with ML-based DDoS Detection and Federated Learning
This application provides OpenFlow switching functionality with:
- Real-time DDoS detection using machine learning
- CICFlowMeter integration for traffic analysis
- Multi-controller support with federated learning
- Automated DDoS mitigation
- Comprehensive logging and monitoring
"""

# Core Ryu imports - simplified for basic functionality
try:
    from ryu.base import app_manager
    from ryu.controller import ofp_event
    from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
    from ryu.controller.handler import set_ev_cls
    from ryu.ofproto import ofproto_v1_3
    from ryu.lib.packet import packet, ethernet, ether_types, arp, ipv4, tcp, udp, icmp
    from ryu.topology import event as topo_event
    from ryu.topology.api import get_switch, get_link, get_host
    RYU_AVAILABLE = True

    # Try to import WSGI - fallback if not available
    try:
        from ryu.app.wsgi import ControllerWSGI
        WSGI_AVAILABLE = True
    except ImportError:
        print("Warning: ControllerWSGI not available. Web interface disabled.")
        WSGI_AVAILABLE = False
        ControllerWSGI = None

except ImportError as e:
    print(f"Warning: Ryu framework not available: {e}")
    RYU_AVAILABLE = False
    WSGI_AVAILABLE = False

import json
import time
import threading
import subprocess
import os
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import socket
import struct
import hashlib

# Optional imports for data analysis
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError:
    print("Warning: numpy/pandas not available. Some features disabled.")
    NUMPY_AVAILABLE = False

# Optional imports for web interface
try:
    from webob import Response
    from webob.static import DirectoryApp
    WEBOB_AVAILABLE = True
except ImportError:
    print("Warning: webob not available. Web interface disabled.")
    WEBOB_AVAILABLE = False
    # Create dummy Response class
    class Response:
        def __init__(self, *args, **kwargs):
            pass

# Conditional decorator for Ryu event handlers
def conditional_set_ev_cls(event_type, dispatcher):
    """Conditional decorator that only applies when Ryu is available"""
    def decorator(func):
        if RYU_AVAILABLE and event_type is not None:
            return set_ev_cls(event_type, dispatcher)(func)
        else:
            return func
    return decorator

# ML and federated learning imports
try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available. ML features disabled.")

# Federated learning imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Advanced federated learning disabled.")


class DDoSDetector:
    """ML-based DDoS detection system with federated learning support"""

    def __init__(self, controller_id="main", is_root=True):
        self.controller_id = controller_id
        self.is_root = is_root
        self.model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.feature_buffer = deque(maxlen=1000)
        self.detection_threshold = 0.7
        self.model_path = f"ddos_model_{controller_id}.pkl"
        self.federated_models = {}
        self.last_training = time.time()
        self.training_interval = 300  # 5 minutes

        # Initialize model
        if ML_AVAILABLE:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.backup_model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Load existing model if available
        self.load_model()

    def extract_flow_features(self, flow_stats, packet_data=None):
        """Extract features from flow statistics for ML analysis"""
        features = {}

        if flow_stats:
            features.update({
                'packet_count': flow_stats.get('packet_count', 0),
                'byte_count': flow_stats.get('byte_count', 0),
                'duration': flow_stats.get('duration_sec', 0),
                'packets_per_second': flow_stats.get('packet_count', 0) / max(flow_stats.get('duration_sec', 1), 1),
                'bytes_per_packet': flow_stats.get('byte_count', 0) / max(flow_stats.get('packet_count', 1), 1),
                'flow_priority': flow_stats.get('priority', 0)
            })

        if packet_data:
            features.update({
                'packet_size': len(packet_data),
                'protocol_type': self._get_protocol_type(packet_data),
                'port_entropy': self._calculate_port_entropy(packet_data)
            })

        return features

    def _get_protocol_type(self, packet_data):
        """Extract protocol type from packet"""
        try:
            pkt = packet.Packet(packet_data)
            if pkt.get_protocol(tcp.tcp):
                return 1  # TCP
            elif pkt.get_protocol(udp.udp):
                return 2  # UDP
            elif pkt.get_protocol(icmp.icmp):
                return 3  # ICMP
            else:
                return 0  # Other
        except:
            return 0

    def _calculate_port_entropy(self, packet_data):
        """Calculate port entropy for anomaly detection"""
        try:
            pkt = packet.Packet(packet_data)
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            udp_pkt = pkt.get_protocol(udp.udp)

            if tcp_pkt:
                return abs(tcp_pkt.src_port - tcp_pkt.dst_port) / 65535.0
            elif udp_pkt:
                return abs(udp_pkt.src_port - udp_pkt.dst_port) / 65535.0
            return 0.0
        except:
            return 0.0

    def detect_ddos(self, features):
        """Detect DDoS attack using ML model"""
        if not ML_AVAILABLE or not NUMPY_AVAILABLE or not self.model:
            return False, 0.0

        try:
            # Convert features to array
            feature_array = np.array(list(features.values())).reshape(1, -1)

            # Scale features
            if hasattr(self.scaler, 'mean_'):
                feature_array = self.scaler.transform(feature_array)

            # Predict anomaly
            anomaly_score = self.model.decision_function(feature_array)[0]
            is_anomaly = self.model.predict(feature_array)[0] == -1

            # Convert to probability
            probability = max(0, min(1, (anomaly_score + 0.5) * 2))

            return is_anomaly and probability > self.detection_threshold, probability
        except Exception as e:
            logging.error(f"DDoS detection error: {e}")
            return False, 0.0

    def update_model(self, new_features, labels=None):
        """Update ML model with new data"""
        if not ML_AVAILABLE:
            return

        self.feature_buffer.append(new_features)

        # Retrain model periodically
        if time.time() - self.last_training > self.training_interval and len(self.feature_buffer) > 50:
            self._retrain_model()
            self.last_training = time.time()

    def _retrain_model(self):
        """Retrain the ML model with buffered data"""
        try:
            if not NUMPY_AVAILABLE or len(self.feature_buffer) < 10:
                return

            # Prepare training data
            X = np.array([list(features.values()) for features in self.feature_buffer])

            # Fit scaler and model
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)

            # Save model
            self.save_model()
            logging.info(f"Model retrained with {len(X)} samples")
        except Exception as e:
            logging.error(f"Model retraining error: {e}")

    def save_model(self):
        """Save ML model to disk"""
        if not ML_AVAILABLE or not self.model:
            return

        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'controller_id': self.controller_id,
                'timestamp': time.time()
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            logging.error(f"Model save error: {e}")

    def load_model(self):
        """Load ML model from disk"""
        if not ML_AVAILABLE or not os.path.exists(self.model_path):
            return

        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.scaler = model_data['scaler']
            logging.info(f"Model loaded for controller {self.controller_id}")
        except Exception as e:
            logging.error(f"Model load error: {e}")


# FEDERATED LEARNING COMMENTED OUT FOR SIMPLIFICATION
# class FederatedLearningManager:
#     """Manages federated learning across multiple controllers"""
#
#     def __init__(self, is_root=True, root_address=None):
#         self.is_root = is_root
#         self.root_address = root_address or "localhost:9999"
#         self.client_models = {}
#         self.global_model_version = 0
#         self.aggregation_interval = 600  # 10 minutes
#         self.last_aggregation = time.time()
#
#         if self.is_root:
#             self._start_aggregation_server()
#
#     def _start_aggregation_server(self):
#         """Start federated learning aggregation server"""
#         def server_thread():
#             try:
#                 server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                 host, port = self.root_address.split(':')
#                 server_socket.bind((host, int(port)))
#                 server_socket.listen(5)
#                 logging.info(f"Federated learning server started on {self.root_address}")
#
#                 while True:
#                     client_socket, addr = server_socket.accept()
#                     threading.Thread(target=self._handle_client, args=(client_socket, addr)).start()
#             except Exception as e:
#                 logging.error(f"Federated learning server error: {e}")
#
#         threading.Thread(target=server_thread, daemon=True).start()
#
#     def _handle_client(self, client_socket, addr):
#         """Handle federated learning client connections"""
#         try:
#             # Receive model update from client
#             data = client_socket.recv(4096)
#             if data:
#                 model_update = pickle.loads(data)
#                 controller_id = model_update.get('controller_id')
#                 self.client_models[controller_id] = model_update
#                 logging.info(f"Received model update from {controller_id}")
#
#                 # Send global model back
#                 global_model = self._get_global_model()
#                 client_socket.send(pickle.dumps(global_model))
#         except Exception as e:
#             logging.error(f"Client handling error: {e}")
#         finally:
#             client_socket.close()
#
#     def _get_global_model(self):
#         """Get current global model"""
#         return {
#             'version': self.global_model_version,
#             'timestamp': time.time(),
#             'model_weights': None  # Placeholder for actual model weights
#         }
#
#     def send_model_update(self, model_data):
#         """Send model update to root controller"""
#         if self.is_root:
#             return
#
#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             host, port = self.root_address.split(':')
#             client_socket.connect((host, int(port)))
#
#             # Send model update
#             client_socket.send(pickle.dumps(model_data))
#
#             # Receive global model
#             response = client_socket.recv(4096)
#             global_model = pickle.loads(response)
#
#             client_socket.close()
#             return global_model
#         except Exception as e:
#             logging.error(f"Model update send error: {e}")
#             return None

# Simplified placeholder for federated learning
class FederatedLearningManager:
    """Simplified placeholder for federated learning - disabled for now"""
    def __init__(self, is_root=True, root_address=None):
        self.is_root = is_root
        self.root_address = root_address
        print("Federated learning disabled - using simplified mode")

    def send_model_update(self, model_data):
        """Placeholder - federated learning disabled"""
        return None


class CICFlowMeterIntegration:
    """Integration with CICFlowMeter for traffic analysis"""

    def __init__(self, output_dir="./traffic_captures"):
        self.output_dir = output_dir
        self.capture_process = None
        self.current_pcap = None
        self.flow_features = deque(maxlen=10000)
        os.makedirs(output_dir, exist_ok=True)

    def start_capture(self, interface="any", duration=300):
        """Start packet capture for CICFlowMeter analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_pcap = os.path.join(self.output_dir, f"capture_{timestamp}.pcap")

        try:
            # Start tcpdump capture
            cmd = [
                "tcpdump", "-i", interface, "-w", self.current_pcap,
                "-G", str(duration), "-W", "1"
            ]
            self.capture_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Started packet capture: {self.current_pcap}")

            # Schedule CICFlowMeter processing
            threading.Timer(duration + 5, self._process_with_cicflowmeter).start()

        except Exception as e:
            logging.error(f"Capture start error: {e}")

    def _process_with_cicflowmeter(self):
        """Process captured traffic with CICFlowMeter"""
        if not self.current_pcap or not os.path.exists(self.current_pcap):
            return

        try:
            output_csv = self.current_pcap.replace('.pcap', '_flows.csv')

            # Run CICFlowMeter
            cmd = ["cicflowmeter", "-f", self.current_pcap, "-c", output_csv]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_csv):
                # Load and process flow features
                self._load_flow_features(output_csv)
                logging.info(f"CICFlowMeter processing completed: {output_csv}")
            else:
                logging.error(f"CICFlowMeter error: {result.stderr}")

        except Exception as e:
            logging.error(f"CICFlowMeter processing error: {e}")

    def _load_flow_features(self, csv_file):
        """Load flow features from CICFlowMeter output"""
        try:
            if not NUMPY_AVAILABLE:
                logging.warning("Pandas not available, skipping CSV processing")
                return

            df = pd.read_csv(csv_file)

            # Extract relevant features for DDoS detection
            for _, row in df.iterrows():
                features = {
                    'flow_duration': row.get('Flow Duration', 0),
                    'total_fwd_packets': row.get('Total Fwd Packets', 0),
                    'total_bwd_packets': row.get('Total Backward Packets', 0),
                    'flow_bytes_per_sec': row.get('Flow Bytes/s', 0),
                    'flow_packets_per_sec': row.get('Flow Packets/s', 0),
                    'flow_iat_mean': row.get('Flow IAT Mean', 0),
                    'fwd_packet_length_mean': row.get('Fwd Packet Length Mean', 0),
                    'bwd_packet_length_mean': row.get('Bwd Packet Length Mean', 0),
                    'label': row.get('Label', 'BENIGN')
                }
                self.flow_features.append(features)

        except Exception as e:
            logging.error(f"Flow features loading error: {e}")

    def get_latest_features(self, count=100):
        """Get latest flow features for analysis"""
        return list(self.flow_features)[-count:] if self.flow_features else []


class FlowMonitorController(app_manager.RyuApp if RYU_AVAILABLE else object):
    if RYU_AVAILABLE:
        OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
        if WSGI_AVAILABLE:
            _CONTEXTS = {'wsgi': ControllerWSGI}
        else:
            _CONTEXTS = {}

    def __init__(self, *args, **kwargs):
        if RYU_AVAILABLE:
            super(FlowMonitorController, self).__init__(*args, **kwargs)
        else:
            print("Warning: Ryu not available, running in simulation mode")

        # Controller configuration
        self.controller_id = kwargs.get('controller_id', f"controller_{int(time.time())}")
        self.is_root = kwargs.get('is_root', True)
        self.root_address = kwargs.get('root_address', "localhost:9999")

        # Data structures for monitoring
        self.mac_to_port = {}
        self.switches = {}
        self.links = {}
        self.hosts = {}
        self.flow_stats = defaultdict(dict)
        self.port_stats = defaultdict(dict)
        self.activity_log = []
        self.start_time = time.time()

        # Statistics collection
        self.stats_reply_count = defaultdict(int)
        self.packet_count = 0
        self.byte_count = 0

        # DDoS detection and mitigation
        self.ddos_detector = DDoSDetector(self.controller_id, self.is_root)
        self.federated_manager = FederatedLearningManager(self.is_root, self.root_address)
        self.cicflow_integration = CICFlowMeterIntegration()

        # DDoS detection state
        self.ddos_alerts = deque(maxlen=1000)
        self.blocked_flows = {}
        self.mitigation_rules = {}
        self.detection_stats = {
            'total_detections': 0,
            'true_positives': 0,
            'false_positives': 0,
            'mitigations_applied': 0
        }

        # Multi-controller coordination
        self.peer_controllers = {}
        self.global_threat_intel = {}

        # Enhanced logging
        self._setup_enhanced_logging()

        # Web server setup - only if WSGI is available
        if WSGI_AVAILABLE and 'wsgi' in kwargs:
            wsgi = kwargs['wsgi']
            wsgi.register(FlowMonitorAPI, {'controller': self})
            print("Web interface enabled")
        else:
            print("Web interface disabled - WSGI not available")

        # Start background threads
        self._start_background_threads()

        self.log_activity('info', f'Enhanced Ryu Flow Monitor Controller started (ID: {self.controller_id})')
        self.log_activity('info', f'Controller mode: {"Root" if self.is_root else "Client"}')

        # Start CICFlowMeter capture (commented out for simplification)
        # self.cicflow_integration.start_capture(duration=300)
        print("CICFlowMeter integration disabled for simplification")

    def _setup_enhanced_logging(self):
        """Setup enhanced logging for DDoS detection and mitigation"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f'ddos_controller_{self.controller_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f'DDoSController_{self.controller_id}')

    def _start_background_threads(self):
        """Start background monitoring and processing threads"""
        # Statistics collection thread
        self.stats_thread = threading.Thread(target=self._collect_stats_periodically)
        self.stats_thread.daemon = True
        self.stats_thread.start()

        # DDoS detection thread
        self.ddos_thread = threading.Thread(target=self._ddos_detection_loop)
        self.ddos_thread.daemon = True
        self.ddos_thread.start()

        # Federated learning sync thread (DISABLED FOR SIMPLIFICATION)
        # if not self.is_root:
        #     self.federated_thread = threading.Thread(target=self._federated_sync_loop)
        #     self.federated_thread.daemon = True
        #     self.federated_thread.start()

        # CICFlowMeter processing thread (DISABLED FOR SIMPLIFICATION)
        # self.cicflow_thread = threading.Thread(target=self._cicflow_processing_loop)
        # self.cicflow_thread.daemon = True
        # self.cicflow_thread.start()
        print("Federated learning and CICFlowMeter threads disabled for simplification")

    def _ddos_detection_loop(self):
        """Main DDoS detection loop"""
        while True:
            try:
                # Get latest flow features from CICFlowMeter
                latest_features = self.cicflow_integration.get_latest_features(50)

                for feature_set in latest_features:
                    # Extract ML features
                    ml_features = self.ddos_detector.extract_flow_features(feature_set)

                    # Detect DDoS
                    is_ddos, confidence = self.ddos_detector.detect_ddos(ml_features)

                    if is_ddos:
                        self._handle_ddos_detection(feature_set, ml_features, confidence)

                    # Update model with new data
                    self.ddos_detector.update_model(ml_features)

                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f"DDoS detection loop error: {e}")
                time.sleep(10)

    # FEDERATED SYNC LOOP DISABLED FOR SIMPLIFICATION
    # def _federated_sync_loop(self):
    #     """Federated learning synchronization loop"""
    #     while True:
    #         try:
    #             if not self.is_root:
    #                 # Send model updates to root controller
    #                 model_data = {
    #                     'controller_id': self.controller_id,
    #                     'model_version': 1,
    #                     'detection_stats': self.detection_stats,
    #                     'timestamp': time.time()
    #                 }
    #
    #                 global_model = self.federated_manager.send_model_update(model_data)
    #                 if global_model:
    #                     self.log_activity('info', f'Received global model update v{global_model.get("version", 0)}')
    #
    #             time.sleep(300)  # Sync every 5 minutes
    #         except Exception as e:
    #             self.logger.error(f"Federated sync error: {e}")
    #             time.sleep(300)

    # CICFLOWMETER PROCESSING LOOP DISABLED FOR SIMPLIFICATION
    # def _cicflow_processing_loop(self):
    #     """CICFlowMeter processing and analysis loop"""
    #     while True:
    #         try:
    #             # Restart capture periodically
    #             self.cicflow_integration.start_capture(duration=300)
    #             time.sleep(310)  # Wait for capture to complete + processing time
    #         except Exception as e:
    #             self.logger.error(f"CICFlowMeter processing error: {e}")
    #             time.sleep(300)

    def _handle_ddos_detection(self, flow_data, ml_features, confidence):
        """Handle detected DDoS attack"""
        timestamp = datetime.now()

        # Create DDoS alert
        alert = {
            'timestamp': timestamp.isoformat(),
            'controller_id': self.controller_id,
            'confidence': confidence,
            'flow_data': flow_data,
            'ml_features': ml_features,
            'attack_type': self._classify_attack_type(ml_features),
            'source_ip': flow_data.get('src_ip', 'unknown'),
            'target_ip': flow_data.get('dst_ip', 'unknown'),
            'mitigation_applied': False
        }

        self.ddos_alerts.append(alert)
        self.detection_stats['total_detections'] += 1

        # Log detection
        self.log_activity('warning',
            f'DDoS DETECTED: {alert["attack_type"]} attack from {alert["source_ip"]} '
            f'to {alert["target_ip"]} (confidence: {confidence:.2f})')

        # Apply mitigation
        mitigation_success = self._apply_ddos_mitigation(alert)
        alert['mitigation_applied'] = mitigation_success

        if mitigation_success:
            self.detection_stats['mitigations_applied'] += 1
            self.log_activity('info', f'DDoS mitigation applied successfully')

        # Share threat intelligence with other controllers
        self._share_threat_intelligence(alert)

    def _classify_attack_type(self, ml_features):
        """Classify the type of DDoS attack based on features"""
        # Simple heuristic-based classification
        pps = ml_features.get('packets_per_second', 0)
        bpp = ml_features.get('bytes_per_packet', 0)
        protocol = ml_features.get('protocol_type', 0)

        if protocol == 1 and pps > 1000:  # TCP
            return "TCP SYN Flood"
        elif protocol == 2 and pps > 500:  # UDP
            return "UDP Flood"
        elif protocol == 3 and pps > 100:  # ICMP
            return "ICMP Flood"
        elif bpp < 100 and pps > 100:
            return "Volumetric Attack"
        else:
            return "Unknown DDoS"

    def _apply_ddos_mitigation(self, alert):
        """Apply DDoS mitigation measures"""
        try:
            source_ip = alert.get('source_ip')
            attack_type = alert.get('attack_type')

            if not source_ip or source_ip == 'unknown':
                return False

            # Create mitigation rule
            rule_id = hashlib.md5(f"{source_ip}_{attack_type}_{time.time()}".encode()).hexdigest()[:8]

            mitigation_rule = {
                'rule_id': rule_id,
                'source_ip': source_ip,
                'action': 'DROP',
                'attack_type': attack_type,
                'timestamp': time.time(),
                'duration': 300  # 5 minutes
            }

            # Apply rule to all connected switches
            for dpid, switch_info in self.switches.items():
                datapath = switch_info['datapath']
                self._install_mitigation_flow(datapath, mitigation_rule)

            self.mitigation_rules[rule_id] = mitigation_rule

            # Schedule rule removal
            threading.Timer(300, self._remove_mitigation_rule, args=[rule_id]).start()

            return True
        except Exception as e:
            self.logger.error(f"Mitigation application error: {e}")
            return False

    def _install_mitigation_flow(self, datapath, rule):
        """Install flow rule for DDoS mitigation"""
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser

            # Create match for source IP
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=rule['source_ip']
            )

            # Drop action
            actions = []  # Empty actions = drop

            # Install flow with high priority
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=1000,  # High priority
                match=match,
                instructions=inst,
                hard_timeout=rule['duration']
            )

            datapath.send_msg(mod)
            self.logger.info(f"Mitigation flow installed on switch {hex(datapath.id)} for {rule['source_ip']}")

        except Exception as e:
            self.logger.error(f"Flow installation error: {e}")

    def _remove_mitigation_rule(self, rule_id):
        """Remove expired mitigation rule"""
        if rule_id in self.mitigation_rules:
            rule = self.mitigation_rules[rule_id]
            del self.mitigation_rules[rule_id]
            self.log_activity('info', f'Mitigation rule {rule_id} expired and removed')

    def _share_threat_intelligence(self, alert):
        """Share threat intelligence with peer controllers"""
        try:
            threat_data = {
                'source_controller': self.controller_id,
                'timestamp': alert['timestamp'],
                'threat_type': alert['attack_type'],
                'source_ip': alert['source_ip'],
                'confidence': alert['confidence'],
                'indicators': {
                    'packets_per_second': alert['ml_features'].get('packets_per_second', 0),
                    'bytes_per_packet': alert['ml_features'].get('bytes_per_packet', 0),
                    'protocol_type': alert['ml_features'].get('protocol_type', 0)
                }
            }

            # Store in global threat intelligence
            threat_id = hashlib.md5(f"{alert['source_ip']}_{alert['timestamp']}".encode()).hexdigest()[:8]
            self.global_threat_intel[threat_id] = threat_data

            # TODO: Send to peer controllers via federated network

        except Exception as e:
            self.logger.error(f"Threat intelligence sharing error: {e}")

    def _validate_model_structure(self, model_data, model_type):
        """Validate uploaded model structure"""
        try:
            if model_type == 'ddos_detector':
                # Check if it's a DDoS detector model
                if isinstance(model_data, dict):
                    required_keys = ['model', 'scaler', 'controller_id', 'timestamp']
                    return all(key in model_data for key in required_keys)
                else:
                    # Check if it's a scikit-learn model
                    return hasattr(model_data, 'predict') or hasattr(model_data, 'decision_function')

            elif model_type == 'federated_model':
                # Check if it's a federated learning model
                if isinstance(model_data, dict):
                    required_keys = ['version', 'model_weights', 'timestamp']
                    return all(key in model_data for key in required_keys)

            return True  # Allow other model types

        except Exception as e:
            self.logger.error(f"Model validation error: {e}")
            return False

    def _save_uploaded_model(self, model_data, model_type, filename, replace_existing):
        """Save uploaded model to disk"""
        try:
            # Create models directory if it doesn't exist
            models_dir = 'models'
            os.makedirs(models_dir, exist_ok=True)

            # Generate unique filename if not replacing
            base_name = os.path.splitext(filename)[0]
            model_path = os.path.join(models_dir, f"{base_name}.pkl")

            if os.path.exists(model_path) and not replace_existing:
                # Generate unique name with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = os.path.join(models_dir, f"{base_name}_{timestamp}.pkl")

            # Save the model
            with open(model_path, 'wb') as f:
                f.write(model_data)

            # Get file info
            stat = os.stat(model_path)

            result = {
                'success': True,
                'message': 'Model uploaded successfully',
                'model_path': model_path,
                'model_name': os.path.splitext(os.path.basename(model_path))[0],
                'size': stat.st_size,
                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }

            self.log_activity('info', f'Model uploaded: {filename} -> {model_path}')
            return result

        except Exception as e:
            self.logger.error(f"Model save error: {e}")
            return {
                'success': False,
                'error': f'Failed to save model: {str(e)}'
            }

    def _update_ddos_model(self, model_data):
        """Update the active DDoS detection model"""
        try:
            if isinstance(model_data, dict):
                # Full model data with scaler
                if 'model' in model_data and 'scaler' in model_data:
                    self.ddos_detector.model = model_data['model']
                    self.ddos_detector.scaler = model_data['scaler']
                    self.log_activity('info', 'DDoS detector model updated from uploaded file')
                    return True
            else:
                # Just the model object
                if hasattr(model_data, 'predict') or hasattr(model_data, 'decision_function'):
                    self.ddos_detector.model = model_data
                    self.log_activity('info', 'DDoS detector model updated (no scaler)')
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Model update error: {e}")
            return False

    def load_model_from_file(self, model_name):
        """Load a specific model from the models directory"""
        try:
            model_path = os.path.join('models', f"{model_name}.pkl")

            if not os.path.exists(model_path):
                self.log_activity('error', f'Model file not found: {model_path}')
                return False

            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            # Update the DDoS detector with the loaded model
            if self._update_ddos_model(model_data):
                self.log_activity('info', f'Successfully loaded model: {model_name}')
                return True
            else:
                self.log_activity('error', f'Failed to update model: {model_name}')
                return False

        except Exception as e:
            self.logger.error(f"Model loading error: {e}")
            self.log_activity('error', f'Error loading model {model_name}: {str(e)}')
            return False

    def export_current_model(self, export_name=None):
        """Export current DDoS detection model"""
        try:
            if not self.ddos_detector.model:
                self.log_activity('warning', 'No active model to export')
                return False

            if not export_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_name = f"exported_model_{self.controller_id}_{timestamp}"

            # Create models directory
            models_dir = 'models'
            os.makedirs(models_dir, exist_ok=True)

            # Prepare model data for export
            model_data = {
                'model': self.ddos_detector.model,
                'scaler': self.ddos_detector.scaler,
                'controller_id': self.controller_id,
                'timestamp': time.time(),
                'export_timestamp': datetime.now().isoformat(),
                'detection_stats': dict(self.detection_stats),
                'model_metrics': {
                    'feature_buffer_size': len(self.ddos_detector.feature_buffer),
                    'last_training': self.ddos_detector.last_training,
                    'detection_threshold': self.ddos_detector.detection_threshold
                }
            }

            # Save exported model
            export_path = os.path.join(models_dir, f"{export_name}.pkl")
            with open(export_path, 'wb') as f:
                pickle.dump(model_data, f)

            self.log_activity('info', f'Model exported to: {export_path}')
            return export_path

        except Exception as e:
            self.logger.error(f"Model export error: {e}")
            self.log_activity('error', f'Failed to export model: {str(e)}')
            return False

    def log_activity(self, level, message):
        """Add entry to activity log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.activity_log.append(entry)

        # Keep only last 100 entries
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)

        self.logger.info(f"[{level.upper()}] {message}")

    @conditional_set_ev_cls(ofp_event.EventOFPSwitchFeatures if RYU_AVAILABLE else None, CONFIG_DISPATCHER if RYU_AVAILABLE else None)
    def switch_features_handler(self, ev):
        """Handle switch connection"""
        if not RYU_AVAILABLE:
            return

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.switches[dpid] = {
            'datapath': datapath,
            'ports': {},
            'flows': 0,
            'connected_time': time.time()
        }

        # Install default flow - send unknown packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        self.log_activity('info', f'Switch {hex(dpid)} connected')

    @conditional_set_ev_cls(ofp_event.EventOFPPacketIn if RYU_AVAILABLE else None, MAIN_DISPATCHER if RYU_AVAILABLE else None)
    def packet_in_handler(self, ev):
        """Enhanced packet-in handler with DDoS detection"""
        if not RYU_AVAILABLE:
            return

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        self.packet_count += 1
        self.byte_count += len(msg.data)

        # Extract packet information for DDoS analysis
        packet_info = self._extract_packet_info(pkt, dpid, in_port)

        # Real-time DDoS detection on packet level
        if packet_info:
            ml_features = self.ddos_detector.extract_flow_features(None, msg.data)
            is_ddos, confidence = self.ddos_detector.detect_ddos(ml_features)

            if is_ddos and confidence > 0.8:  # High confidence threshold for packet-level detection
                self.log_activity('warning',
                    f'Real-time DDoS detected: {packet_info.get("src_ip", "unknown")} -> '
                    f'{packet_info.get("dst_ip", "unknown")} (confidence: {confidence:.2f})')

                # Immediate mitigation for high-confidence detections
                if packet_info.get('src_ip'):
                    self._apply_immediate_mitigation(datapath, packet_info['src_ip'])
                return  # Drop the packet

        # Learn MAC address
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule for known destinations
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)

            # Check if we have a valid buffer_id
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

            if self.switches[dpid]:
                self.switches[dpid]['flows'] += 1

        # Handle special packet types with enhanced analysis
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            self._handle_arp(pkt, dpid, in_port, packet_info)
        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            self._handle_ip(pkt, dpid, in_port, packet_info)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def _extract_packet_info(self, pkt, dpid, in_port):
        """Extract detailed packet information for analysis"""
        try:
            info = {
                'dpid': dpid,
                'in_port': in_port,
                'timestamp': time.time(),
                'packet_size': len(pkt.data) if hasattr(pkt, 'data') else 0
            }

            # Extract IP information
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            if ip_pkt:
                info.update({
                    'src_ip': ip_pkt.src,
                    'dst_ip': ip_pkt.dst,
                    'protocol': ip_pkt.proto,
                    'ttl': ip_pkt.ttl,
                    'tos': ip_pkt.tos
                })

                # Extract TCP information
                tcp_pkt = pkt.get_protocol(tcp.tcp)
                if tcp_pkt:
                    info.update({
                        'src_port': tcp_pkt.src_port,
                        'dst_port': tcp_pkt.dst_port,
                        'tcp_flags': tcp_pkt.bits,
                        'window_size': tcp_pkt.window_size,
                        'protocol_type': 'TCP'
                    })

                # Extract UDP information
                udp_pkt = pkt.get_protocol(udp.udp)
                if udp_pkt:
                    info.update({
                        'src_port': udp_pkt.src_port,
                        'dst_port': udp_pkt.dst_port,
                        'protocol_type': 'UDP'
                    })

                # Extract ICMP information
                icmp_pkt = pkt.get_protocol(icmp.icmp)
                if icmp_pkt:
                    info.update({
                        'icmp_type': icmp_pkt.type,
                        'icmp_code': icmp_pkt.code,
                        'protocol_type': 'ICMP'
                    })

            return info
        except Exception as e:
            self.logger.error(f"Packet info extraction error: {e}")
            return None

    def _apply_immediate_mitigation(self, datapath, source_ip):
        """Apply immediate mitigation for high-confidence DDoS detection"""
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser

            # Create match for source IP
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=source_ip
            )

            # Drop action with high priority and short timeout
            actions = []
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=2000,  # Very high priority
                match=match,
                instructions=inst,
                hard_timeout=60  # 1 minute immediate block
            )

            datapath.send_msg(mod)
            self.log_activity('info', f'Immediate mitigation applied for {source_ip} on switch {hex(datapath.id)}')

        except Exception as e:
            self.logger.error(f"Immediate mitigation error: {e}")

    def _handle_arp(self, pkt, dpid, in_port):
        """Handle ARP packets"""
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self.log_activity('info', f'ARP request from {arp_pkt.src_ip} on switch {hex(dpid)}')

    def _handle_ip(self, pkt, dpid, in_port):
        """Handle IP packets"""
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt:
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            udp_pkt = pkt.get_protocol(udp.udp)
            icmp_pkt = pkt.get_protocol(icmp.icmp)

            if tcp_pkt:
                if tcp_pkt.dst_port == 80 or tcp_pkt.src_port == 80:
                    self.log_activity('info', f'HTTP traffic detected: {ip_pkt.src} -> {ip_pkt.dst}')
            elif icmp_pkt:
                self.log_activity('info', f'ICMP packet: {ip_pkt.src} -> {ip_pkt.dst}')

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """Add flow entry to switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                  priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                  match=match, instructions=inst)
        datapath.send_msg(mod)

    @conditional_set_ev_cls(ofp_event.EventOFPFlowStatsReply if RYU_AVAILABLE else None, MAIN_DISPATCHER if RYU_AVAILABLE else None)
    def flow_stats_reply_handler(self, ev):
        """Handle flow statistics reply"""
        if not RYU_AVAILABLE:
            return

        flows = []
        for stat in ev.msg.body:
            flows.append({
                'priority': stat.priority,
                'match': str(stat.match),
                'actions': str(stat.instructions),
                'packet_count': stat.packet_count,
                'byte_count': stat.byte_count,
                'duration_sec': stat.duration_sec
            })

        self.flow_stats[ev.msg.datapath.id] = flows

    @conditional_set_ev_cls(ofp_event.EventOFPPortStatsReply if RYU_AVAILABLE else None, MAIN_DISPATCHER if RYU_AVAILABLE else None)
    def port_stats_reply_handler(self, ev):
        """Handle port statistics reply"""
        if not RYU_AVAILABLE:
            return

        ports = []
        for stat in ev.msg.body:
            ports.append({
                'port_no': stat.port_no,
                'rx_packets': stat.rx_packets,
                'tx_packets': stat.tx_packets,
                'rx_bytes': stat.rx_bytes,
                'tx_bytes': stat.tx_bytes,
                'rx_errors': stat.rx_errors,
                'tx_errors': stat.tx_errors
            })

        self.port_stats[ev.msg.datapath.id] = ports

    @conditional_set_ev_cls(topo_event.EventSwitchEnter if RYU_AVAILABLE else None, None)
    def switch_enter_handler(self, ev):
        """Handle switch enter event"""
        if not RYU_AVAILABLE:
            return

        switch = ev.switch
        dpid = switch.dp.id
        self.log_activity('info', f'Switch {hex(dpid)} entered topology')

    @conditional_set_ev_cls(topo_event.EventSwitchLeave if RYU_AVAILABLE else None, None)
    def switch_leave_handler(self, ev):
        """Handle switch leave event"""
        if not RYU_AVAILABLE:
            return

        switch = ev.switch
        dpid = switch.dp.id
        if dpid in self.switches:
            del self.switches[dpid]
        self.log_activity('warning', f'Switch {hex(dpid)} left topology')

    @conditional_set_ev_cls(topo_event.EventLinkAdd if RYU_AVAILABLE else None, None)
    def link_add_handler(self, ev):
        """Handle link add event"""
        if not RYU_AVAILABLE:
            return

        link = ev.link
        src_dpid = link.src.dpid
        dst_dpid = link.dst.dpid
        self.links[f"{src_dpid}-{dst_dpid}"] = link
        self.log_activity('info', f'Link added: {hex(src_dpid)} -> {hex(dst_dpid)}')

    @conditional_set_ev_cls(topo_event.EventLinkDelete if RYU_AVAILABLE else None, None)
    def link_delete_handler(self, ev):
        """Handle link delete event"""
        if not RYU_AVAILABLE:
            return

        link = ev.link
        src_dpid = link.src.dpid
        dst_dpid = link.dst.dpid
        link_key = f"{src_dpid}-{dst_dpid}"
        if link_key in self.links:
            del self.links[link_key]
        self.log_activity('warning', f'Link deleted: {hex(src_dpid)} -> {hex(dst_dpid)}')

    def _collect_stats_periodically(self):
        """Collect statistics from switches periodically"""
        while True:
            try:
                for dpid, switch_info in self.switches.items():
                    datapath = switch_info['datapath']
                    self._request_stats(datapath)
                time.sleep(10)  # Collect stats every 10 seconds
            except Exception as e:
                self.logger.error(f"Error collecting stats: {e}")
                time.sleep(10)

    def _request_stats(self, datapath):
        """Request statistics from switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Request flow stats
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        # Request port stats
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    def get_switches_info(self):
        """Get information about all switches"""
        switches_info = []
        for dpid, switch_info in self.switches.items():
            switches_info.append({
                'id': hex(dpid),
                'status': 'Active',
                'flows': len(self.flow_stats.get(dpid, [])),
                'ports': len(self.port_stats.get(dpid, [])),
                'uptime': int(time.time() - switch_info['connected_time'])
            })
        return switches_info

    def get_flow_stats_all(self):
        """Get flow statistics from all switches"""
        all_flows = []
        for dpid, flows in self.flow_stats.items():
            for flow in flows:
                flow['switch_id'] = hex(dpid)
                all_flows.append(flow)
        return all_flows

    def get_network_stats(self):
        """Get overall network statistics"""
        total_flows = sum(len(flows) for flows in self.flow_stats.values())
        uptime = int(time.time() - self.start_time)

        return {
            'switch_count': len(self.switches),
            'flow_count': total_flows,
            'packet_count': self.packet_count,
            'byte_count': self.byte_count,
            'link_count': len(self.links),
            'uptime': uptime
        }

    def get_topology_data(self):
        """Get network topology data"""
        return {
            'switches': list(self.switches.keys()),
            'links': [
                {
                    'src': int(link.src.dpid),
                    'dst': int(link.dst.dpid),
                    'src_port': link.src.port_no,
                    'dst_port': link.dst.port_no
                }
                for link in self.links.values()
            ]
        }


class FlowMonitorAPI(object):
    """REST API for Flow Monitor"""

    def __init__(self, req, link, data, **config):
        super(FlowMonitorAPI, self).__init__()
        self.controller = data['controller']

        # Set up CORS headers for web interface
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }

    def switches(self, req, **kwargs):
        """Get switches information"""
        switches = self.controller.get_switches_info()
        return Response(content_type='application/json',
                       body=json.dumps(switches),
                       headers=self.headers)

    def flows(self, req, **kwargs):
        """Get flow statistics"""
        flows = self.controller.get_flow_stats_all()
        return Response(content_type='application/json',
                       body=json.dumps(flows),
                       headers=self.headers)

    def stats(self, req, **kwargs):
        """Get network statistics"""
        stats = self.controller.get_network_stats()
        return Response(content_type='application/json',
                       body=json.dumps(stats),
                       headers=self.headers)

    def topology(self, req, **kwargs):
        """Get topology information"""
        topology = self.controller.get_topology_data()
        return Response(content_type='application/json',
                       body=json.dumps(topology),
                       headers=self.headers)

    def logs(self, req, **kwargs):
        """Get activity logs"""
        logs = self.controller.activity_log
        return Response(content_type='application/json',
                       body=json.dumps(logs),
                       headers=self.headers)

    def port_stats(self, req, **kwargs):
        """Get port statistics"""
        dpid = kwargs.get('dpid')
        if dpid:
            dpid = int(dpid, 16)  # Convert hex string to int
            port_stats = self.controller.port_stats.get(dpid, [])
        else:
            port_stats = dict(self.controller.port_stats)

        return Response(content_type='application/json',
                       body=json.dumps(port_stats),
                       headers=self.headers)

    def ddos_alerts(self, req, **kwargs):
        """Get DDoS detection alerts"""
        alerts = [dict(alert) for alert in self.controller.ddos_alerts]
        return Response(content_type='application/json',
                       body=json.dumps(alerts),
                       headers=self.headers)

    def ddos_stats(self, req, **kwargs):
        """Get DDoS detection statistics"""
        stats = dict(self.controller.detection_stats)
        stats.update({
            'active_mitigations': len(self.controller.mitigation_rules),
            'blocked_flows': len(self.controller.blocked_flows),
            'controller_id': self.controller.controller_id,
            'is_root': self.controller.is_root,
            'threat_intel_count': len(self.controller.global_threat_intel)
        })
        return Response(content_type='application/json',
                       body=json.dumps(stats),
                       headers=self.headers)

    def mitigation_rules(self, req, **kwargs):
        """Get active mitigation rules"""
        rules = dict(self.controller.mitigation_rules)
        return Response(content_type='application/json',
                       body=json.dumps(rules),
                       headers=self.headers)

    def threat_intel(self, req, **kwargs):
        """Get threat intelligence data"""
        intel = dict(self.controller.global_threat_intel)
        return Response(content_type='application/json',
                       body=json.dumps(intel),
                       headers=self.headers)

    def cicflow_features(self, req, **kwargs):
        """Get CICFlowMeter features"""
        count = int(kwargs.get('count', 100))
        features = self.controller.cicflow_integration.get_latest_features(count)
        return Response(content_type='application/json',
                       body=json.dumps(features),
                       headers=self.headers)

    def federated_status(self, req, **kwargs):
        """Get federated learning status"""
        status = {
            'is_root': self.controller.is_root,
            'controller_id': self.controller.controller_id,
            'root_address': self.controller.root_address,
            'client_models': len(self.controller.federated_manager.client_models) if self.controller.is_root else 0,
            'global_model_version': self.controller.federated_manager.global_model_version,
            'last_sync': getattr(self.controller.federated_manager, 'last_aggregation', 0)
        }
        return Response(content_type='application/json',
                       body=json.dumps(status),
                       headers=self.headers)

    def upload_model(self, req, **kwargs):
        """Upload ML model (.pkl file)"""
        try:
            if req.method != 'POST':
                return Response(status=405, body='Method not allowed')

            # Check if file is uploaded
            if 'model_file' not in req.POST:
                return Response(status=400,
                               body=json.dumps({'error': 'No model file provided'}),
                               content_type='application/json',
                               headers=self.headers)

            model_file = req.POST['model_file']
            model_type = req.POST.get('model_type', 'ddos_detector')
            replace_existing = req.POST.get('replace_existing', 'false').lower() == 'true'

            # Validate file extension
            if not model_file.filename.endswith('.pkl'):
                return Response(status=400,
                               body=json.dumps({'error': 'Only .pkl files are allowed'}),
                               content_type='application/json',
                               headers=self.headers)

            # Read and validate model file
            model_data = model_file.file.read()

            try:
                # Attempt to load the pickle file to validate it
                import pickle
                loaded_model = pickle.loads(model_data)

                # Validate model structure
                if not self._validate_model_structure(loaded_model, model_type):
                    return Response(status=400,
                                   body=json.dumps({'error': 'Invalid model structure'}),
                                   content_type='application/json',
                                   headers=self.headers)

            except Exception as e:
                return Response(status=400,
                               body=json.dumps({'error': f'Invalid pickle file: {str(e)}'}),
                               content_type='application/json',
                               headers=self.headers)

            # Save the model
            result = self._save_uploaded_model(model_data, model_type, model_file.filename, replace_existing)

            if result['success']:
                # Update the controller's model if it's a DDoS detector model
                if model_type == 'ddos_detector':
                    self._update_ddos_model(loaded_model)

                return Response(status=200,
                               body=json.dumps(result),
                               content_type='application/json',
                               headers=self.headers)
            else:
                return Response(status=400,
                               body=json.dumps(result),
                               content_type='application/json',
                               headers=self.headers)

        except Exception as e:
            self.controller.logger.error(f"Model upload error: {e}")
            return Response(status=500,
                           body=json.dumps({'error': f'Internal server error: {str(e)}'}),
                           content_type='application/json',
                           headers=self.headers)

    def download_model(self, req, **kwargs):
        """Download ML model (.pkl file)"""
        try:
            model_type = kwargs.get('model_type', 'ddos_detector')
            model_name = kwargs.get('model_name', None)

            # Get model file path
            if model_name:
                model_path = os.path.join('models', f"{model_name}.pkl")
            else:
                model_path = f"ddos_model_{self.controller.controller_id}.pkl"

            if not os.path.exists(model_path):
                return Response(status=404,
                               body=json.dumps({'error': 'Model file not found'}),
                               content_type='application/json',
                               headers=self.headers)

            # Read model file
            with open(model_path, 'rb') as f:
                model_data = f.read()

            # Prepare response headers for file download
            headers = dict(self.headers)
            headers.update({
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename="{os.path.basename(model_path)}"',
                'Content-Length': str(len(model_data))
            })

            return Response(body=model_data, headers=headers)

        except Exception as e:
            self.controller.logger.error(f"Model download error: {e}")
            return Response(status=500,
                           body=json.dumps({'error': f'Internal server error: {str(e)}'}),
                           content_type='application/json',
                           headers=self.headers)

    def list_models(self, req, **kwargs):
        """List available ML models"""
        try:
            models = []

            # List models in models directory
            models_dir = 'models'
            if os.path.exists(models_dir):
                for filename in os.listdir(models_dir):
                    if filename.endswith('.pkl'):
                        filepath = os.path.join(models_dir, filename)
                        stat = os.stat(filepath)

                        models.append({
                            'name': filename[:-4],  # Remove .pkl extension
                            'filename': filename,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'type': 'uploaded'
                        })

            # Add current controller model
            current_model_path = f"ddos_model_{self.controller.controller_id}.pkl"
            if os.path.exists(current_model_path):
                stat = os.stat(current_model_path)
                models.append({
                    'name': f"current_{self.controller.controller_id}",
                    'filename': current_model_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': 'current',
                    'active': True
                })

            return Response(content_type='application/json',
                           body=json.dumps({'models': models}),
                           headers=self.headers)

        except Exception as e:
            self.controller.logger.error(f"Model listing error: {e}")
            return Response(status=500,
                           body=json.dumps({'error': f'Internal server error: {str(e)}'}),
                           content_type='application/json',
                           headers=self.headers)

    def delete_model(self, req, **kwargs):
        """Delete ML model"""
        try:
            if req.method != 'DELETE':
                return Response(status=405, body='Method not allowed')

            model_name = kwargs.get('model_name')
            if not model_name:
                return Response(status=400,
                               body=json.dumps({'error': 'Model name required'}),
                               content_type='application/json',
                               headers=self.headers)

            # Prevent deletion of current active model
            if model_name == f"current_{self.controller.controller_id}":
                return Response(status=400,
                               body=json.dumps({'error': 'Cannot delete active model'}),
                               content_type='application/json',
                               headers=self.headers)

            model_path = os.path.join('models', f"{model_name}.pkl")

            if not os.path.exists(model_path):
                return Response(status=404,
                               body=json.dumps({'error': 'Model not found'}),
                               content_type='application/json',
                               headers=self.headers)

            # Delete the model file
            os.remove(model_path)

            self.controller.log_activity('info', f'Model {model_name} deleted')

            return Response(content_type='application/json',
                           body=json.dumps({'success': True, 'message': f'Model {model_name} deleted'}),
                           headers=self.headers)

        except Exception as e:
            self.controller.logger.error(f"Model deletion error: {e}")
            return Response(status=500,
                           body=json.dumps({'error': f'Internal server error: {str(e)}'}),
                           content_type='application/json',
                           headers=self.headers)


# URL routing configuration
def create_wsgi_app(controller_instance):
    """Create WSGI application with URL routing"""
    from ryu.app.wsgi import WSGIApplication, route

    # Create the WSGI application
    wsgi_app = WSGIApplication()

    # Register routes with enhanced DDoS monitoring endpoints
    wsgi_app.register(FlowMonitorAPI, {'controller': controller_instance})

    return wsgi_app

# Enhanced route mappings for DDoS monitoring and model management
ROUTE_MAPPINGS = {
    '/switches': 'switches',
    '/flows': 'flows',
    '/stats': 'stats',
    '/topology': 'topology',
    '/logs': 'logs',
    '/port_stats': 'port_stats',
    '/port_stats/{dpid}': 'port_stats',
    '/ddos/alerts': 'ddos_alerts',
    '/ddos/stats': 'ddos_stats',
    '/ddos/mitigation': 'mitigation_rules',
    '/ddos/threats': 'threat_intel',
    '/cicflow/features': 'cicflow_features',
    '/cicflow/features/{count}': 'cicflow_features',
    '/federated/status': 'federated_status',
    '/models/upload': 'upload_model',
    '/models/download/{model_name}': 'download_model',
    '/models/list': 'list_models',
    '/models/delete/{model_name}': 'delete_model'
}


if __name__ == '__main__':
    # Example of how to run this controller
    print("Ryu Flow Monitor Controller")
    print("Usage: ryu-manager flow_monitor_controller.py --observe-links")
    print("")
    print("REST API Endpoints:")
    print("  GET /switches     - Get switch information")
    print("  GET /flows        - Get flow statistics")
    print("  GET /stats        - Get network statistics")
    print("  GET /topology     - Get topology data")
    print("  GET /logs         - Get activity logs")
    print("  GET /port_stats   - Get port statistics")
