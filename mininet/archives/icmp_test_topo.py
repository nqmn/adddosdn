#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Three-tier topology (8 hosts, 6 switches) for Python 2.7.

All OVS switches are forced to use OpenFlow 1.3 so they work with
`icmp_monitor.py`.

Run with:
    sudo python three_tier_topology_py27.py
"""

import os, time
from functools import partial
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


class ThreeTierTopo(Topo):
    "Two tier-1 switches → four tier-2 switches → eight hosts."

    def build(self):
        # Tier 1
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Tier 2
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # Eight hosts
        hosts = [self.addHost('h%s' % i) for i in range(1, 9)]

        # Core links
        self.addLink(s1, s2)       # inter-tier-1 link
        self.addLink(s1, s3); self.addLink(s1, s4)
        self.addLink(s2, s5); self.addLink(s2, s6)

        # Host links (two per tier-2 switch)
        self.addLink(hosts[0], s3); self.addLink(hosts[1], s3)
        self.addLink(hosts[2], s4); self.addLink(hosts[3], s4)
        self.addLink(hosts[4], s5); self.addLink(hosts[5], s5)
        self.addLink(hosts[6], s6); self.addLink(hosts[7], s6)


def run():
    setLogLevel('info')
    os.system('mn -c')                     # clean previous runs

    # Force OVS 1.3
    switch13 = partial(OVSSwitch, protocols='OpenFlow13')

    topo = ThreeTierTopo()
    net  = Mininet(topo=topo, switch=switch13, controller=None)
    net.addController('c0', controller=RemoteController,
                      ip='127.0.0.1', port=6633)
    net.start()

    print "⌛ Waiting 5 s for switches to negotiate..."
    time.sleep(5)

    print "✅ Simple ping test:"
    net.pingAll()

    CLI(net)
    net.stop()


if __name__ == '__main__':
    run()

