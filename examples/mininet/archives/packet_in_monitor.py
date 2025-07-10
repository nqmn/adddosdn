from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
import time
from collections import defaultdict

class PacketInFloodMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    THRESHOLD = 100  # Packet-In threshold per TIME_WINDOW per MAC
    TIME_WINDOW = 5  # seconds

    def __init__(self, *args, **kwargs):
        super(PacketInFloodMonitor, self).__init__(*args, **kwargs)
        self.packetin_counts = defaultdict(lambda: [0, time.time()])  # src_mac: [count, start_time]

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        src_mac = eth.src

        count, start_time = self.packetin_counts[src_mac]
        now = time.time()
        if now - start_time > self.TIME_WINDOW:
            # Reset for new time window
            self.packetin_counts[src_mac] = [1, now]
        else:
            count += 1
            self.packetin_counts[src_mac][0] = count
            if count > self.THRESHOLD:
                self.logger.error(f"Packet-In flood detected from {src_mac}: {count} Packet-Ins in {self.TIME_WINDOW}s")
            else:
                self.logger.info(f"Packet-In from {src_mac}: {count} in current window")

