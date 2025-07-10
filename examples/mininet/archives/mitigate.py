from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from collections import defaultdict
import time

class FloodMitigator(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    THRESHOLD = 100         # Packet-Ins per window to trigger block
    TIME_WINDOW = 5         # Seconds per window
    BLOCK_DURATION = 60     # Block duration in seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.packetin_counts = defaultdict(lambda: [0, time.time()])  # src_mac: [count, window_start_time]
        self.blocked_macs = {}  # src_mac: unblock_time

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None:
            return
        src = eth.src
        now = time.time()

        # Check if already blocked (optional: refresh block if seen again)
        unblock_time = self.blocked_macs.get(src, 0)
        if now < unblock_time:
            self.logger.warning(f"[Mitigator] Blocked MAC {src} tried to send traffic. Still blocked for {int(unblock_time-now)}s.")
            self._install_block_flow(datapath, src)
            return

        # Flood Detection Logic
        count, start_time = self.packetin_counts[src]
        if now - start_time > self.TIME_WINDOW:
            # Start new time window
            self.packetin_counts[src] = [1, now]
        else:
            count += 1
            self.packetin_counts[src][0] = count
            if count > self.THRESHOLD:
                self.logger.error(f"[Mitigator] Packet-In flood from {src}! Blocking for {self.BLOCK_DURATION} seconds.")
                self.blocked_macs[src] = now + self.BLOCK_DURATION
                self._install_block_flow(datapath, src)
                # Optionally: reset counter for next time window
                self.packetin_counts[src] = [0, now]

    def _install_block_flow(self, datapath, src_mac):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        match = parser.OFPMatch(eth_src=src_mac)
        actions = []  # Drop (no actions)
        # Set hard_timeout for auto-expiry
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=100,
            match=match,
            instructions=[parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)],
            hard_timeout=self.BLOCK_DURATION
        )
        datapath.send_msg(mod)
        self.logger.info(f"[Mitigator] Drop flow for {src_mac} installed for {self.BLOCK_DURATION} seconds.")

