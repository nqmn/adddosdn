#!/usr/bin/env python3

import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import subprocess

class SimpleTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(s1, s2)

def run():
    print("Cleaning up Mininet environment...")
    os.system('sudo mn -c > /dev/null 2>&1')

    print("Starting Ryu controller...")
    # Launch Ryu controller with simple_switch_13 app in verbose mode, in background
    ryu_process = subprocess.Popen([
        'ryu-manager', '--verbose', 'ryu.app.simple_switch_13'
    ])

    # Wait a few seconds to ensure controller is up before starting Mininet
    time.sleep(3)

    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=None)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    net.start()

    os.system('sudo tcpdump -i s1-eth1 -w s1-eth1.pcap &')

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