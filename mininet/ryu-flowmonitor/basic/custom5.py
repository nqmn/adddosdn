#!/usr/bin/env python

import re
import sys
from sys import exit
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.link import Intf
from mininet.node import RemoteController

def checkIntf(intf):
    "Make sure intf exists and is not configured."
    from mininet.util import quietRun
    config = quietRun('ifconfig %s 2>/dev/null' % intf, shell=True)
    if not config:
        error('Error:', intf, 'does not exist!\n')
        exit(1)
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', config)
    if ips:
        error('Error:', intf, 'has an IP address,'
              'and is probably in use!\n')
        exit(1)

if __name__ == '__main__':
    setLogLevel('info')

    # Get hardware interface name (default to ens32)
    intfName = sys.argv[1] if len(sys.argv) > 1 else 'ens32'
    info('*** Connecting to hw intf: %s\n' % intfName)
    checkIntf(intfName)

    info('*** Creating network\n')
    net = Mininet(controller=None, waitConnected=True)

    # Add remote controller
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.159.132', port=6633)

    # Add a switch
    s1 = net.addSwitch('s1')

    # Attach the hardware interface to the switch
    info('*** Adding hardware interface %s to switch %s\n' % (intfName, s1.name))
    Intf(intfName, node=s1)

    # Add 4 hosts: h2 to h5 with custom IPs
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')

    # Connect hosts to the switch
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    info('*** Starting network\n')
    net.start()

    info('*** Network is ready. Hosts:\n')
    for h in [h2, h3, h4, h5]:
        info('%s: %s\n' % (h.name, h.IP()))

    CLI(net)
    net.stop()

