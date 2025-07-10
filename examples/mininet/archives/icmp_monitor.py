#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Ryu app that:
1) Installs a flow rule to send ICMP packets to the controller.
2) Installs a lower-priority table-miss rule to forward other traffic normally.
3) Logs every ICMP packet it sees and then floods it.

Tested with Python 3.7+ + Ryu >= 4.34.
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, icmp
from ryu.lib.packet.ethernet import ETH_TYPE_IP
from ryu.lib.packet.ipv4 import IPPROTO_ICMP

# For type hinting
from ryu.controller.controller import Datapath
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch, OFPActionOutput, OFPInstructionActions, OFPFlowMod


class ICMPMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # ------------------------------------------------------------------ #
    # Switch handshake                                                   #
    # ------------------------------------------------------------------ #
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev: ofp_event.EventOFPSwitchFeatures):
        """Install rules: ICMP to controller, others OFPP_NORMAL."""
        datapath: Datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # 1. Install a flow to send ICMP (IPv4) packets to the controller
        #    eth_type=0x0800 for IPv4, ip_proto=1 for ICMP
        match_icmp = parser.OFPMatch(eth_type=ETH_TYPE_IP, ip_proto=IPPROTO_ICMP)
        actions_to_controller = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                                      ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 10, match_icmp, actions_to_controller) # Priority 10

        # 2. Install a table-miss flow for non-ICMP traffic to be forwarded normally
        #    This lets the switch handle other traffic using its traditional pipeline.
        match_all = parser.OFPMatch() # Matches everything
        actions_normal = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 0, match_all, actions_normal) # Lowest priority (0)

        self.logger.info(f"Switch {datapath.id:016x} connected. ICMP monitoring enabled.")
        self.logger.info(f"  - ICMP (IPv4) packets will be sent to controller (Priority 10).")
        self.logger.info(f"  - Other packets will be forwarded via OFPP_NORMAL (Priority 0).")

    # ------------------------------------------------------------------ #
    # Flow-mod helper                                                    #
    # ------------------------------------------------------------------ #
    def add_flow(self, datapath: Datapath, priority: int, match: OFPMatch, actions: list):
        """Helper to add a flow entry to the switch."""
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)
        self.logger.debug(f"FlowMod sent to {datapath.id:016x}: priority={priority}, match={match}, actions={actions}")


    # ------------------------------------------------------------------ #
    # Packet-in handler                                                  #
    # ------------------------------------------------------------------ #
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev: ofp_event.EventOFPPacketIn):
        """Handle incoming ICMP packets."""
        msg = ev.msg
        datapath: Datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Get the input port from the match structure of the PacketIn message
        # This is more reliable than trying to parse it from raw packet data if available
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)

        # We expect only ICMP packets due to the flow rule, but good to double check
        ip_hdr = pkt.get_protocol(ipv4.ipv4)
        icmp_hdr = pkt.get_protocol(icmp.icmp)

        if ip_hdr and icmp_hdr:
            self.logger.info(f"💡 ICMP on switch {datapath.id:016x} (in_port {in_port}): "
                             f"{ip_hdr.src} → {ip_hdr.dst} "
                             f"(type={icmp_hdr.type} code={icmp_hdr.code})")

            # To allow ICMP communication to succeed, flood the packet.
            # For more complex scenarios, you might install a specific flow
            # or use L2 learning logic to determine the output port.
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

            # If buffer_id is valid, use it to avoid resending packet data
            buffer_id = msg.buffer_id
            data_to_send = None
            if buffer_id == ofproto.OFP_NO_BUFFER:
                data_to_send = msg.data

            out = parser.OFPPacketOut(datapath=datapath,
                                      buffer_id=buffer_id,
                                      in_port=in_port,
                                      actions=actions,
                                      data=data_to_send)
            datapath.send_msg(out)
            self.logger.debug(f"Sent PacketOut to flood ICMP from {datapath.id:016x}")
        else:
            # This case should ideally not be hit if flow rules are set correctly
            self.logger.warning(f"Unexpected packet_in on switch {datapath.id:016x} (in_port {in_port}): {pkt}")
