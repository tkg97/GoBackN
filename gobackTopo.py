from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.log import setLogLevel, info

setLogLevel('info')

net = Mininet(controller=RemoteController)
# We have set up a remote controller at ip = 127.0.0.1 , port = 6633

info('adding Controller\n')
net.addController('c0')

info('Adding Hosts\n')
host1 = net.addHost("h1", ip='10.0.2.1')
host2 = net.addHost("h2", ip='10.0.2.2')

info('Adding Switches\n')
switch = net.addSwitch("s1", cls=OVSSwitch)

info('Adding Links\n')

net.addLink(host1, switch)
net.addLink(host2, switch)
# The above links can be customized by setting bandwidth and delay etc

net.start()
CLI(net);

host2.cmd('./server.py')
host1.cmd('./client.py')

net.stop()