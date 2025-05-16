#!/usr/bin/env python3

import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import subprocess

class ThreeTierTopo(Topo):
    def build(self):
        # Tier 1 switches (connected to controller)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Tier 2 switches (connected to tier 1)
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # Hosts connected to tier 2 switches (2 hosts per switch)
        hosts = []
        for i in range(1, 9):
            hosts.append(self.addHost(f'h{i}'))

        # Connect tier 1 switches to controller (done by Mininet)
        # Connect tier 2 switches to tier 1
        self.addLink(s1, s3)
        self.addLink(s1, s4)
        self.addLink(s2, s5)
        self.addLink(s2, s6)

        # Connect hosts to tier 2 switches
        # Hosts 1 & 2 -> s3
        self.addLink(hosts[0], s3)
        self.addLink(hosts[1], s3)

        # Hosts 3 & 4 -> s4
        self.addLink(hosts[2], s4)
        self.addLink(hosts[3], s4)

        # Hosts 5 & 6 -> s5
        self.addLink(hosts[4], s5)
        self.addLink(hosts[5], s5)

        # Hosts 7 & 8 -> s6
        self.addLink(hosts[6], s6)
        self.addLink(hosts[7], s6)

def run():
    print("Cleaning up Mininet environment...")
    os.system('sudo mn -c > /dev/null 2>&1')

    print("Starting Ryu controller...")
    ryu_process = subprocess.Popen([
        'ryu-manager', '--verbose', 'ryu.app.simple_switch_13'
    ])

    print("Waiting 5 seconds for RYU controller to start...")
    time.sleep(5)

    topo = ThreeTierTopo()
    net = Mininet(topo=topo, controller=None)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    net.start()

    print("Waiting 5 seconds for controller to stabilize...")
    time.sleep(5)

    print("Testing network connectivity")
    net.pingAll()

    CLI(net)

    print("Stopping network...")
    net.stop()

    print("Stopping Ryu controller...")
    ryu_process.terminate()
    ryu_process.wait()

if __name__ == '__main__':
    setLogLevel('info')
    run()
