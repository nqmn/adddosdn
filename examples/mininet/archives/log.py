from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.lib.packet import packet, ethernet, ipv4, arp, icmp, tcp, udp
import time

class PacketInLogger(app_manager.RyuApp):
    OFP_VERSIONS = [0x04]  # OpenFlow 1.3

    LOGFILE = 'packet_in_log.txt'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Open the log file in append mode
        self.logfile = open(self.LOGFILE, "a")

    def __del__(self):
        self.logfile.close()

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = msg.match.get('in_port', None)
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        src = eth.src if eth else "?"
        dst = eth.dst if eth else "?"
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # Try to extract more info
        ip = pkt.get_protocol(ipv4.ipv4)
        arp_pkt = pkt.get_protocol(arp.arp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        protocol = ""
        details = ""
        if arp_pkt:
            protocol = "ARP"
            details = f"arp_op={arp_pkt.opcode} src_ip={arp_pkt.src_ip} dst_ip={arp_pkt.dst_ip}"
        elif ip:
            protocol = "IPv4"
            details = f"ip_src={ip.src} ip_dst={ip.dst} proto={ip.proto}"
            if icmp_pkt:
                protocol += "/ICMP"
            elif tcp_pkt:
                protocol += "/TCP"
                details += f" tcp_sport={tcp_pkt.src_port} tcp_dport={tcp_pkt.dst_port}"
            elif udp_pkt:
                protocol += "/UDP"
                details += f" udp_sport={udp_pkt.src_port} udp_dport={udp_pkt.dst_port}"
        else:
            protocol = "ETH_ONLY"
        
        log_line = f"{timestamp} | dpid={dpid} in_port={in_port} src={src} dst={dst} proto={protocol} {details}\n"
        self.logfile.write(log_line)
        self.logfile.flush()
        # Optional: also print to terminal
        self.logger.info(log_line.strip())

