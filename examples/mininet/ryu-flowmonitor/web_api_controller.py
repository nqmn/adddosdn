#!/usr/bin/env python3
"""
Web API Controller for SDN Flow Monitor
Provides REST API endpoints for monitoring and DDoS detection
"""

import json
import time
from datetime import datetime
from wsgi_framework import ControllerBase, Response, route, WSGIApplication


class FlowMonitorAPI(ControllerBase):
    """REST API for Flow Monitor with DDoS Detection"""

    def __init__(self, req, link, data, **config):
        super(FlowMonitorAPI, self).__init__(req, link, data, **config)
        self.controller = data['controller'] if data else None
        
        # Set up CORS headers for web interface
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }

    def _json_response(self, data, status=200):
        """Create JSON response with CORS headers"""
        return Response(
            body=json.dumps(data, indent=2),
            status=status,
            content_type='application/json',
            headers=self.headers
        )

    def _error_response(self, message, status=500):
        """Create error response"""
        return self._json_response({'error': message}, status)

    @route('index', '/', methods=['GET'])
    def index(self, req, **kwargs):
        """API index with available endpoints"""
        endpoints = {
            'api_info': 'SDN Flow Monitor API with DDoS Detection',
            'version': '1.0',
            'endpoints': {
                '/': 'This index',
                '/status': 'Controller status',
                '/switches': 'Switch information',
                '/flows': 'Flow statistics',
                '/stats': 'Network statistics',
                '/topology': 'Network topology',
                '/logs': 'Activity logs',
                '/ddos/alerts': 'DDoS detection alerts',
                '/ddos/stats': 'DDoS detection statistics',
                '/ddos/mitigation': 'Active mitigation rules',
                '/ddos/threats': 'Threat intelligence',
                '/cicflow/features': 'CICFlowMeter features',
                '/federated/status': 'Federated learning status',
                '/models/list': 'Available ML models'
            }
        }
        return self._json_response(endpoints)

    @route('status', '/status', methods=['GET'])
    def status(self, req, **kwargs):
        """Get controller status"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            status = self.controller.get_status()
            status['timestamp'] = datetime.now().isoformat()
            return self._json_response(status)
        except Exception as e:
            return self._error_response(f"Failed to get status: {str(e)}")

    @route('switches', '/switches', methods=['GET'])
    def switches(self, req, **kwargs):
        """Get switches information"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            # Get switches info if available
            if hasattr(self.controller, 'get_switches_info'):
                switches = self.controller.get_switches_info()
            else:
                switches = {
                    'switches': list(self.controller.switches.keys()) if hasattr(self.controller, 'switches') else [],
                    'count': len(self.controller.switches) if hasattr(self.controller, 'switches') else 0
                }
            return self._json_response(switches)
        except Exception as e:
            return self._error_response(f"Failed to get switches: {str(e)}")

    @route('flows', '/flows', methods=['GET'])
    def flows(self, req, **kwargs):
        """Get flow statistics"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            if hasattr(self.controller, 'get_flow_stats_all'):
                flows = self.controller.get_flow_stats_all()
            else:
                flows = {
                    'flows': dict(self.controller.flow_stats) if hasattr(self.controller, 'flow_stats') else {},
                    'count': len(self.controller.flow_stats) if hasattr(self.controller, 'flow_stats') else 0
                }
            return self._json_response(flows)
        except Exception as e:
            return self._error_response(f"Failed to get flows: {str(e)}")

    @route('stats', '/stats', methods=['GET'])
    def stats(self, req, **kwargs):
        """Get network statistics"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            if hasattr(self.controller, 'get_network_stats'):
                stats = self.controller.get_network_stats()
            else:
                stats = {
                    'packet_count': getattr(self.controller, 'packet_count', 0),
                    'byte_count': getattr(self.controller, 'byte_count', 0),
                    'uptime': int(time.time() - self.controller.start_time) if hasattr(self.controller, 'start_time') else 0
                }
            return self._json_response(stats)
        except Exception as e:
            return self._error_response(f"Failed to get stats: {str(e)}")

    @route('topology', '/topology', methods=['GET'])
    def topology(self, req, **kwargs):
        """Get topology information"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            if hasattr(self.controller, 'get_topology_data'):
                topology = self.controller.get_topology_data()
            else:
                topology = {
                    'switches': list(self.controller.switches.keys()) if hasattr(self.controller, 'switches') else [],
                    'links': list(self.controller.links.keys()) if hasattr(self.controller, 'links') else [],
                    'hosts': list(self.controller.hosts.keys()) if hasattr(self.controller, 'hosts') else []
                }
            return self._json_response(topology)
        except Exception as e:
            return self._error_response(f"Failed to get topology: {str(e)}")

    @route('logs', '/logs', methods=['GET'])
    def logs(self, req, **kwargs):
        """Get activity logs"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            logs = {
                'logs': list(self.controller.activity_log) if hasattr(self.controller, 'activity_log') else [],
                'count': len(self.controller.activity_log) if hasattr(self.controller, 'activity_log') else 0
            }
            return self._json_response(logs)
        except Exception as e:
            return self._error_response(f"Failed to get logs: {str(e)}")

    @route('ddos_alerts', '/ddos/alerts', methods=['GET'])
    def ddos_alerts(self, req, **kwargs):
        """Get DDoS detection alerts"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            alerts = {
                'alerts': list(self.controller.ddos_alerts) if hasattr(self.controller, 'ddos_alerts') else [],
                'count': len(self.controller.ddos_alerts) if hasattr(self.controller, 'ddos_alerts') else 0
            }
            return self._json_response(alerts)
        except Exception as e:
            return self._error_response(f"Failed to get DDoS alerts: {str(e)}")

    @route('ddos_stats', '/ddos/stats', methods=['GET'])
    def ddos_stats(self, req, **kwargs):
        """Get DDoS detection statistics"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            stats = dict(self.controller.detection_stats) if hasattr(self.controller, 'detection_stats') else {}
            stats.update({
                'active_mitigations': len(self.controller.mitigation_rules) if hasattr(self.controller, 'mitigation_rules') else 0,
                'blocked_flows': len(self.controller.blocked_flows) if hasattr(self.controller, 'blocked_flows') else 0,
                'controller_id': getattr(self.controller, 'controller_id', 'unknown'),
                'is_root': getattr(self.controller, 'is_root', False),
                'threat_intel_count': len(self.controller.global_threat_intel) if hasattr(self.controller, 'global_threat_intel') else 0
            })
            return self._json_response(stats)
        except Exception as e:
            return self._error_response(f"Failed to get DDoS stats: {str(e)}")

    @route('mitigation_rules', '/ddos/mitigation', methods=['GET'])
    def mitigation_rules(self, req, **kwargs):
        """Get active mitigation rules"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            rules = {
                'rules': dict(self.controller.mitigation_rules) if hasattr(self.controller, 'mitigation_rules') else {},
                'count': len(self.controller.mitigation_rules) if hasattr(self.controller, 'mitigation_rules') else 0
            }
            return self._json_response(rules)
        except Exception as e:
            return self._error_response(f"Failed to get mitigation rules: {str(e)}")

    @route('threat_intel', '/ddos/threats', methods=['GET'])
    def threat_intel(self, req, **kwargs):
        """Get threat intelligence data"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            intel = {
                'threats': dict(self.controller.global_threat_intel) if hasattr(self.controller, 'global_threat_intel') else {},
                'count': len(self.controller.global_threat_intel) if hasattr(self.controller, 'global_threat_intel') else 0
            }
            return self._json_response(intel)
        except Exception as e:
            return self._error_response(f"Failed to get threat intel: {str(e)}")

    @route('cicflow_features', '/cicflow/features', methods=['GET'])
    def cicflow_features(self, req, **kwargs):
        """Get CICFlowMeter features"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            count = int(kwargs.get('count', 100))
            if hasattr(self.controller, 'cicflow_integration'):
                features = self.controller.cicflow_integration.get_latest_features(count)
            else:
                features = []
            
            return self._json_response({
                'features': features,
                'count': len(features)
            })
        except Exception as e:
            return self._error_response(f"Failed to get CICFlow features: {str(e)}")

    @route('federated_status', '/federated/status', methods=['GET'])
    def federated_status(self, req, **kwargs):
        """Get federated learning status"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            if hasattr(self.controller, 'federated_manager'):
                status = {
                    'is_root': getattr(self.controller.federated_manager, 'is_root', False),
                    'root_address': getattr(self.controller.federated_manager, 'root_address', None),
                    'client_models': len(getattr(self.controller.federated_manager, 'client_models', {})),
                    'global_model_version': getattr(self.controller.federated_manager, 'global_model_version', 0)
                }
            else:
                status = {'status': 'Federated learning not available'}
            
            return self._json_response(status)
        except Exception as e:
            return self._error_response(f"Failed to get federated status: {str(e)}")

    @route('models_list', '/models/list', methods=['GET'])
    def models_list(self, req, **kwargs):
        """List available ML models"""
        if not self.controller:
            return self._error_response("Controller not available")
        
        try:
            models = {
                'models': [],
                'ddos_detector_available': hasattr(self.controller, 'ddos_detector'),
                'ml_available': getattr(self.controller, 'ml_available', False) if hasattr(self.controller, 'ml_available') else False
            }
            return self._json_response(models)
        except Exception as e:
            return self._error_response(f"Failed to list models: {str(e)}")


def create_wsgi_app(controller_instance):
    """Create WSGI application with controller"""
    wsgi_app = WSGIApplication()
    wsgi_app.register(FlowMonitorAPI, {'controller': controller_instance})
    return wsgi_app
