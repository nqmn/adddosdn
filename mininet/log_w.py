from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from scapy.utils import PcapWriter
from scapy.all import Ether  # Import Ether

class PacketInPcapDumper(app_manager.RyuApp):
    OFP_VERSIONS = [0x04]  # OpenFlow 1.3

    PCAP_FILE = "packet_in.pcap"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pcap_writer = PcapWriter(self.PCAP_FILE, append=True, sync=True)

    def __del__(self):
        if hasattr(self, "pcap_writer") and self.pcap_writer:
            self.pcap_writer.close()

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        data = msg.data
        # Wrap the raw bytes as a Scapy Ether object
        pkt = Ether(data)
        self.pcap_writer.write(pkt)
        self.logger.info("PacketIn written to %s (%d bytes)", self.PCAP_FILE, len(data))

