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
# global variables
transmit_window = 7
receive_window = 1
expected_ack = 0
expected_pkt = 0
frame_to_send = 0
drop_probability = 0.1
q = queue.Queue(maxsize=transmit_window)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = '10.0.2.2'
port = 6654

address = (ip, port)

server.bind(address)

server.listen(1)

client, addr = server.accept()

while True:
	data = client.recv(1024)
	if (data=="hey"):
		client.send("Hi")
	else :
		client.send("Invalid")
		client.close()
		break

def pkt_sender(pkt_received, ack_received, resend_pkts):
	start_time = time.time()*1000
	i=0
	global transmit_window
	global frame_to_send
	global q  
	while(true):
		cur_time = time.time()*1000
		if(abs(abs(cur_time-start_time)-2.5)<0.01):
			# create and send packet here
			if(!q.full()):
				
			client.send()



def pkt_receiver(pkt_received, ack_received, resend_pkts):



def ack_receiver(pkt_received, ack_received, resend_pkts):




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

    logging.debug('Waiting before calling Event.set()')
    time.sleep(3)
    e.set()
    logging.debug('Event is set')

