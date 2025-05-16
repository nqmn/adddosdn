from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
# from ryu.lib.packet import ether_types # This import was present but not used
# from ryu.controller import dpset # This import is no longer needed as DEAD_DISPATCHER is directly imported

import time
from threading import Thread
import logging # Import the logging module

class CombinedApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(CombinedApp, self).__init__(*args, **kwargs)
        
        # Explicitly set the logger level for this application to DEBUG.
        # This ensures that INFO and DEBUG messages from this app are processed.
        self.logger.setLevel(logging.DEBUG)
        self.logger.info('[INIT] CombinedApp initializing...')
        
        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_interval = 5  # seconds
        
        self.logger.info('[INIT] Starting monitor thread...')
        self.monitor_thread = Thread(target=self._monitor)
        self.monitor_thread.daemon = True # Ensure thread exits when main app exits
        self.monitor_thread.start()
        self.logger.info('[INIT] Monitor thread started.')
        self.logger.info('[INIT] CombinedApp initialization complete.')

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.info("[STATE CHANGE] Register datapath: %016x", datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.info("[STATE CHANGE] Unregister datapath: %016x", datapath.id)
                del self.datapaths[datapath.id]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.logger.info("[SWITCH FEATURES] Received from switch: %016x", datapath.id)

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("[SWITCH FEATURES] Table-miss flow installed for %016x.", datapath.id)
        self.logger.info("[SWITCH FEATURES] Switch connected: %s", datapath.id) # Original log

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Log details of the flow being added
        self.logger.debug("[ADD FLOW] dpid=%016x, priority=%s, match=%s, actions=%s, buffer_id=%s",
                         datapath.id, priority, match, actions, buffer_id)

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)
        self.logger.debug("[ADD FLOW] FlowMod sent to %016x.", datapath.id)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_protocol = pkt.get_protocol(ethernet.ethernet)

        if not eth_protocol:
            self.logger.debug("[PACKET IN] Non-Ethernet packet received on dpid=%s, port=%s. Ignoring.", 
                              datapath.id, in_port)
            return

        eth = eth_protocol
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.logger.info("[PACKET IN] dpid=%s src=%s dst=%s in_port=%s", dpid, src, dst, in_port)

        self.mac_to_port.setdefault(dpid, {})
        if self.mac_to_port[dpid].get(src) != in_port:
             self.logger.info("[LEARN] dpid=%s: MAC %s learned on port %s", dpid, src, in_port)
             self.mac_to_port[dpid][src] = in_port


        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            
            # Use msg.buffer_id if available, otherwise None (which add_flow handles)
            current_buffer_id = msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            self.add_flow(datapath, 1, match, actions, current_buffer_id)
            self.logger.info("[INSTALL FLOW] dpid=%s: %s -> %s (port %s)", dpid, src, dst, out_port)
        else:
            self.logger.info("[FLOOD] dpid=%s: Destination MAC %s unknown. Flooding packet from port %s.", dpid, dst, in_port)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=msg.buffer_id,
                                  in_port=in_port,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)
        self.logger.debug("[PACKET OUT] Sent for dpid=%s, in_port=%s, actions=%s", dpid, in_port, actions)


    def _request_stats(self, datapath):
        self.logger.debug("[STATS REQUEST] Sending flow stats request to: %016x", datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        datapath = ev.msg.datapath
        dpid = datapath.id

        self.logger.info('[STATS REPLY] Flow stats for datapath: %016x', dpid)
        self.logger.info('  table_id  in_port  eth_dst            eth_src            packets    bytes      duration_sec')
        self.logger.info('  --------  -------  -----------------  -----------------  ---------  ---------- -----------')
        
        sorted_stats = sorted([flow for flow in body if flow.priority == 1],
                              key=lambda f: (f.match.get('in_port', 'N/A'), 
                                             f.match.get('eth_dst', 'N/A'),
                                             f.match.get('eth_src', 'N/A')))
        if not sorted_stats:
            self.logger.info("  (No flow stats with priority 1 to display for this datapath)")

        for stat in sorted_stats:
            self.logger.info('  %8x  %7s  %17s  %17s  %9d  %10d %d',
                             stat.table_id,
                             stat.match.get('in_port', 'N/A'),
                             stat.match.get('eth_dst', 'N/A'),
                             stat.match.get('eth_src', 'N/A'),
                             stat.packet_count,
                             stat.byte_count,
                             stat.duration_sec)

    def _monitor(self):
        self.logger.info('[MONITOR] Monitor thread started and entering main loop.')
        try:
            while True:
                # Create a copy of datapaths to iterate over, in case it's modified elsewhere
                for dp_id, dp in list(self.datapaths.items()):
                    self.logger.debug("[MONITOR] Requesting stats for datapath: %016x", dp_id)
                    self._request_stats(dp)
                time.sleep(self.monitor_interval)
        except Exception as e:
            self.logger.error("[MONITOR] Exception in monitor thread: %s", e, exc_info=True)
        finally:
            self.logger.info("[MONITOR] Monitor thread exiting.")


