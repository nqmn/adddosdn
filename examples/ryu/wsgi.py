from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication, route, websocket, Response
import json
from ryu.lib import hub

# REST API URLs
url_patterns = {
    'hello': '/hello',
    'flows': '/flows',
    'ports': '/ports',
    'packets': '/packets',
    'events': '/ws/events',
}


class RestController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.api_app = data

    @route('hello', url_patterns['hello'], methods=['GET'])
    def hello(self, req, **kwargs):
        return Response(content_type='text/plain', body='Hello from SDN API')

    @route('flows', url_patterns['flows'], methods=['GET'])
    def flows(self, req, **kwargs):
        flows = self.api_app.collected_flows
        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    @route('ports', url_patterns['ports'], methods=['GET'])
    def ports(self, req, **kwargs):
        ports = self.api_app.collected_ports
        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    @route('packets', url_patterns['packets'], methods=['GET'])
    def packets(self, req, **kwargs):
        packets = self.api_app.packet_ins
        body = json.dumps(packets)
        return Response(content_type='application/json', body=body)


class WebSocketController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.api_app = data

    @websocket('events', url_patterns['events'])
    def websocket_handler(self, ws):
        self.api_app.ws_clients.append(ws)

        while True:
            msg = ws.wait()
            if msg is None:
                break
        self.api_app.ws_clients.remove(ws)


class APIApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(APIApp, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']

        self.ws_clients = []
        self.collected_flows = []
        self.collected_ports = []
        self.packet_ins = []

        wsgi.register(RestController, self)
        wsgi.register(WebSocketController, self)

        self.datapaths = {}
        self.polling_thread = hub.spawn(self._polling_loop)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        self.datapaths[datapath.id] = datapath

    def _polling_loop(self):
        while True:
            for dp in list(self.datapaths.values()):
                self._request_flow_stats(dp)
                self._request_port_stats(dp)
            hub.sleep(5)

    def _request_flow_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    def _request_port_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        dpid = ev.msg.datapath.id
        flow_stats = []
        for stat in ev.msg.body:
            flow_stats.append({
                'dpid': dpid,
                'priority': stat.priority,
                'match': dict(stat.match),
                'duration_sec': stat.duration_sec,
                'packet_count': stat.packet_count,
                'byte_count': stat.byte_count,
                'actions': [str(a) for a in stat.instructions],
            })
        self.collected_flows = flow_stats

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        dpid = ev.msg.datapath.id
        port_stats = []
        for stat in ev.msg.body:
            port_stats.append({
                'dpid': dpid,
                'port_no': stat.port_no,
                'rx_packets': stat.rx_packets,
                'tx_packets': stat.tx_packets,
                'rx_bytes': stat.rx_bytes,
                'tx_bytes': stat.tx_bytes,
                'rx_errors': stat.rx_errors,
                'tx_errors': stat.tx_errors,
            })
        self.collected_ports = port_stats

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = msg.match['in_port']

        self.packet_ins.append({
            'dpid': dpid,
            'in_port': in_port,
            'data_len': msg.msg_len,
        })
        if len(self.packet_ins) > 1000:
            self.packet_ins = self.packet_ins[-1000:]
