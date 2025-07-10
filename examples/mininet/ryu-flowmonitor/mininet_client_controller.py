#!/usr/bin/env python3
"""
Mininet Client Controller for Multi-Controller DDoS Detection
This controller runs on the Mininet server and communicates with the root controller
for federated learning and coordinated DDoS detection.
"""

import sys
import os
import argparse

# Import the main controller
from flow_monitor_controller import FlowMonitorController

class MininetClientController(FlowMonitorController):
    """Client controller for Mininet server with switch-level DDoS detection"""
    
    def __init__(self, *args, **kwargs):
        # Set client-specific configuration
        kwargs['is_root'] = False
        kwargs['controller_id'] = kwargs.get('controller_id', f"mininet_client_{os.getpid()}")
        kwargs['root_address'] = kwargs.get('root_address', "192.168.1.100:9999")  # Default root server
        
        super(MininetClientController, self).__init__(*args, **kwargs)
        
        self.log_activity('info', f'Mininet Client Controller initialized')
        self.log_activity('info', f'Root controller: {self.root_address}')
        
        # Enhanced switch-level monitoring
        self.switch_ddos_stats = {}
        self.local_threat_cache = {}
        
    def _handle_ddos_detection(self, flow_data, ml_features, confidence):
        """Enhanced DDoS handling for switch-level detection"""
        # Call parent method
        super()._handle_ddos_detection(flow_data, ml_features, confidence)
        
        # Additional switch-level processing
        switch_id = flow_data.get('dpid', 'unknown')
        
        # Update switch-specific statistics
        if switch_id not in self.switch_ddos_stats:
            self.switch_ddos_stats[switch_id] = {
                'detections': 0,
                'mitigations': 0,
                'last_attack': None,
                'attack_types': {}
            }
        
        stats = self.switch_ddos_stats[switch_id]
        stats['detections'] += 1
        stats['last_attack'] = flow_data.get('timestamp')
        
        attack_type = self._classify_attack_type(ml_features)
        stats['attack_types'][attack_type] = stats['attack_types'].get(attack_type, 0) + 1
        
        self.log_activity('info', 
            f'Switch {switch_id} DDoS stats updated: {stats["detections"]} total detections')
    
    def get_switch_ddos_stats(self):
        """Get switch-level DDoS statistics"""
        return dict(self.switch_ddos_stats)
    
    def sync_with_root(self):
        """Synchronize with root controller"""
        try:
            # Prepare comprehensive update
            update_data = {
                'controller_id': self.controller_id,
                'controller_type': 'mininet_client',
                'switch_count': len(self.switches),
                'detection_stats': self.detection_stats,
                'switch_ddos_stats': self.switch_ddos_stats,
                'active_mitigations': len(self.mitigation_rules),
                'timestamp': time.time(),
                'model_metrics': self._get_model_metrics()
            }
            
            # Send to root controller
            global_model = self.federated_manager.send_model_update(update_data)
            
            if global_model:
                self.log_activity('info', 
                    f'Synchronized with root controller - Global model v{global_model.get("version", 0)}')
                return True
            else:
                self.log_activity('warning', 'Failed to synchronize with root controller')
                return False
                
        except Exception as e:
            self.logger.error(f"Root synchronization error: {e}")
            return False
    
    def _get_model_metrics(self):
        """Get current model performance metrics"""
        if not hasattr(self.ddos_detector, 'model') or not self.ddos_detector.model:
            return {}
        
        return {
            'feature_buffer_size': len(self.ddos_detector.feature_buffer),
            'last_training': self.ddos_detector.last_training,
            'detection_threshold': self.ddos_detector.detection_threshold,
            'model_type': type(self.ddos_detector.model).__name__
        }


def main():
    """Main function to run the Mininet client controller"""
    parser = argparse.ArgumentParser(description='Mininet Client Controller for DDoS Detection')
    parser.add_argument('--controller-id', default=None, 
                       help='Unique controller ID')
    parser.add_argument('--root-address', default='192.168.1.100:9999',
                       help='Root controller address (host:port)')
    parser.add_argument('--wsapi-port', type=int, default=8081,
                       help='REST API port')
    parser.add_argument('--ofp-tcp-listen-port', type=int, default=6634,
                       help='OpenFlow listen port')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Prepare controller arguments
    controller_kwargs = {
        'controller_id': args.controller_id,
        'root_address': args.root_address
    }
    
    print(f"Starting Mininet Client Controller...")
    print(f"Controller ID: {args.controller_id or 'auto-generated'}")
    print(f"Root Controller: {args.root_address}")
    print(f"REST API Port: {args.wsapi_port}")
    print(f"OpenFlow Port: {args.ofp_tcp_listen_port}")
    
    # Import Ryu manager
    from ryu.cmd import manager
    
    # Set up Ryu arguments
    sys.argv = [
        'ryu-manager',
        '--wsapi-port', str(args.wsapi_port),
        '--ofp-tcp-listen-port', str(args.ofp_tcp_listen_port),
        '--observe-links',
        __file__
    ]
    
    if args.verbose:
        sys.argv.append('--verbose')
    
    # Run the controller
    manager.main()


if __name__ == '__main__':
    main()
