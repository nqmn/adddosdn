#!/usr/bin/env python3
"""
Ryu Controller Application with REST API for Flow Monitor
This application provides OpenFlow switching functionality with REST APIs
for the web-based flow monitor to connect and retrieve real-time data.
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, arp, ipv4, tcp, udp, icmp
from ryu.topology import event as topo_event
from ryu.topology.api import get_switch, get_link, get_host
from ryu.app.wsgi import ControllerWSGI
# BGP not needed for this application

import json
import time
import threading
from datetime import datetime
from collections import defaultdict
from webob import Response
from webob.static import DirectoryApp

class FlowMonitorController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': ControllerWSGI}

    def __init__(self, *args, **kwargs):
        super(FlowMonitorController, self).__init__(*args, **kwargs)

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

        # Web server setup
        wsgi = kwargs['wsgi']
        wsgi.register(FlowMonitorAPI, {'controller': self})

        # Start statistics collection thread
        self.stats_thread = threading.Thread(target=self._collect_stats_periodically)
        self.stats_thread.daemon = True
        self.stats_thread.start()

        self.log_activity('info', 'Ryu Flow Monitor Controller started')

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

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection"""
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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle packet-in messages"""
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

        # Handle special packet types
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            self._handle_arp(pkt, dpid, in_port)
        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            self._handle_ip(pkt, dpid, in_port)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

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

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        """Handle flow statistics reply"""
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

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        """Handle port statistics reply"""
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

    @set_ev_cls(topo_event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        """Handle switch enter event"""
        switch = ev.switch
        dpid = switch.dp.id
        self.log_activity('info', f'Switch {hex(dpid)} entered topology')

    @set_ev_cls(topo_event.EventSwitchLeave)
    def switch_leave_handler(self, ev):
        """Handle switch leave event"""
        switch = ev.switch
        dpid = switch.dp.id
        if dpid in self.switches:
            del self.switches[dpid]
        self.log_activity('warning', f'Switch {hex(dpid)} left topology')

    @set_ev_cls(topo_event.EventLinkAdd)
    def link_add_handler(self, ev):
        """Handle link add event"""
        link = ev.link
        src_dpid = link.src.dpid
        dst_dpid = link.dst.dpid
        self.links[f"{src_dpid}-{dst_dpid}"] = link
        self.log_activity('info', f'Link added: {hex(src_dpid)} -> {hex(dst_dpid)}')

    @set_ev_cls(topo_event.EventLinkDelete)
    def link_delete_handler(self, ev):
        """Handle link delete event"""
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


# URL routing configuration
def create_wsgi_app(controller_instance):
    """Create WSGI application with URL routing"""
    from ryu.app.wsgi import WSGIApplication, route

    # Create the WSGI application
    wsgi_app = WSGIApplication()

    # Create API instance with controller reference
    api_instance = FlowMonitorAPI(None, None, {'controller': controller_instance})

    # Register routes
    wsgi_app.register(FlowMonitorAPI, {'controller': controller_instance})

    return wsgi_app


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
