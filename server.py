import sys
from collections import namedtuple
import pickle
import threading
import inspect
import time
import signal
import socket
import logging
import queue
from frame import data_frame, ack_frame
import pickle

# global variables
transmit_window = 7
receive_window = 1
expected_ack = 0
expected_pkt = 0
frame_to_send = 0

packet_drop_probability = 0.1
ack_drop_probability = 0.05

q = queue.Queue(maxsize=transmit_window)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '10.0.2.2'
port = 6654
address = (ip, port)
server.bind(address)
server.listen(1)

def or_set(self):
    self._set()
    self.changed()

def or_clear(self):
    self._clear()
    self.changed()

def orify(e, changed_callback):
    e._set = e.set
    e._clear = e.clear
    e.changed = changed_callback
    e.set = lambda: or_set(e)
    e.clear = lambda: or_clear(e)

def OrEvent(*events):
    or_event = threading.Event()
    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()
    for e in events:
        orify(e, changed)
    changed()
    return or_event


def pkt_sender(pkt_received, ack_received, resend_pkts):
	client, __addr = server.accept()

	start_time = time.time()*1000
	i=0
	global transmit_window
	global frame_to_send
	global q
	tempq = queue.Queue(maxsize=transmit_window)
	while(True):
		cur_time = time.time()*1000
		if(abs(abs(cur_time-start_time)-2.5*i)<0.01):
			i += 1
			if(~q.full()):
				if (tempq.empty()) :
					# create and send packet here
					new_packet = data_frame(frame_to_send % transmit_window)
					frame_to_send = (frame_to_send + 1)%transmit_window
					new_packet_string = pickle.dumps(new_packet)
					q.put(new_packet) #Insert a packet into queue
					client.send(new_packet_string)
				else :
					#Get that pack from tempq top
					new_packet = tempq.get()
					new_packet_string = pickle.dumps(new_packet)
					q.put(new_packet) #Insert a packet into queue
					client.send(new_packet_string)

			else  :
				or_event = OrEvent(ack_received, resend_pkts)
				__or_event_is_set = or_event.wait()
				if (ack_received.is_set()) :
					# create and send packet here
					new_packet = data_frame(frame_to_send % transmit_window)
					frame_to_send = (frame_to_send + 1)%transmit_window
					new_packet_string = pickle.dumps(new_packet)
					q.put(new_packet) #Insert a packet into queue
					client.send(new_packet_string)
				else :
					#Resend all the buffered packets
					tempq.queue.clear()
					while (q.empty==False) :
						tempq.put(q.get())




def pkt_receiver(pkt_received, ack_received, resend_pkts):
	pass


def ack_receiver(pkt_received, ack_received, resend_pkts):
	pass


if __name__ == '__main__':
    pkt_received = threading.Event()
    ack_received = threading.Event()
    resend_pkts = threading.Event()

    pkt_sender = threading.Thread(name='pkt_sender', 
                      target=pkt_sender,
                      args=(pkt_received, ack_received, resend_pkts))
    pkt_sender.start()

    pkt_receiver = threading.Thread(name='pkt_receiver', 
                      target=pkt_receiver, 
                      args=(pkt_received, ack_received, resend_pkts))
    pkt_receiver.start()


    ack_receiver = threading.Thread(name='ack_receiver', 
                      target=ack_receiver, 
                      args=(pkt_received, ack_received, resend_pkts))
    ack_receiver.start()