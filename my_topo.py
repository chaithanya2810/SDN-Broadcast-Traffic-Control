from mininet.topo import Topo

class MyProjectTopo(Topo):
    def build(self):
        # Add 1 switch
        s1 = self.addSwitch('s1')
        # Add 3 hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        # Connect them
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

topos = {'myproject': (lambda: MyProjectTopo())}
