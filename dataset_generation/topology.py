from mininet.topo import Topo

class CustomTopology(Topo):
    """Custom topology with one switch and six hosts."""
    def build(self, **_opts):
        # Add a switch
        s1 = self.addSwitch('s1')

        # Add 6 hosts with IP addresses 10.0.0.1 to 10.0.0.6
        for i in range(1, 7):
            host = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
            self.addLink(host, s1)