from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os

log = core.getLogger()

class switch (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):
        ''' Add your logic here ... '''
	msg = of.ofp_flow_mod()
	msg.match.in_port = 1
	msg.actions.append(of.ofp_action_output(port=2))
	msg1 = of.ofp_flow_mod()
	msg1.match.in_port = 2
	msg1.actions.append(of.ofp_action_output(port=1))
	event.connection.send(msg)	
	event.connection.send(msg1)

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(switch)