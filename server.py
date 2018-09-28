import sys
import pickle
import threading
import inspect
import time
import signal
import socket
import logging
import pickle
import select
import random
from myqueue import Queue
from collections import namedtuple
from frame import data_frame, ack_frame

# global variables
transmit_window = 7
max_seq_num = transmit_window + 1
receive_window = 1
expected_ack = 0
expected_pkt = 0
frame_to_send = 0
timer_duration = 50000 #in milliseconds

q = Queue(transmit_window)
time_stamp_q = Queue(transmit_window)
tempq = Queue(transmit_window)

packet_drop_probability = 0.1
ack_drop_probability = 0.05

sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '169.254.224.230'
port = 6654
address = (ip, port)
sender_server.bind(address)
sender_server.listen(1)
client_receiver, __addr_receiver = sender_server.accept()

client_sender = socket.socket()
while True:
	try:
		client_sender.connect(('169.254.224.230', 6653))
		break
	except TimeoutError:
		pass

base_time = time.time()*1000

def should_drop(threshold) :
	temp = random.uniform(0,1)
	if(temp<=threshold) : return True
	else : return False

def respond_to_pck_resending(resend_pkts):
	#Resend all the buffered packets
	global tempq
	global time_stamp_q
	global q
	tempq.clear()
	time_stamp_q.clear()
	while (q.empty()==False) :
		tempq.put(q.get())
	resend_pkts.clear()

def pkt_sender(resend_pkts):
	global transmit_window
	global frame_to_send
	global q
	global client_receiver
	global max_seq_num
	while(True):
		if(resend_pkts.is_set()) : continue
		cur_time = time.time()*1000 - base_time
		if(q.full() == False):
			# print ("** %d **" %(q.size()))
			if (tempq.empty()) :
				# create and send packet here
				new_packet = data_frame(frame_to_send % max_seq_num)
				cur_time = time.time()*1000 - base_time

				print ("generated packet %d, at time %f" %(frame_to_send, cur_time))

				new_packet_string = pickle.dumps(new_packet)
				q.put(new_packet) #Insert a packet into queue
				time_stamp_q.put(cur_time)
				__ready = select.select([],[client_receiver],[])
				if (should_drop(packet_drop_probability) == False) :
					print ("packet %d, at time %f, sent successfully" %(frame_to_send, cur_time))
					client_receiver.send(new_packet_string)
				frame_to_send = (frame_to_send + 1)%max_seq_num
			else :
				#Get that pack from tempq top
				new_packet = tempq.get()
				cur_time = time.time()*1000	- base_time				
				
				print ("Trying to resend the packet number %d at time %f" %(new_packet.data_num, cur_time))

				new_packet_string = pickle.dumps(new_packet)
				q.put(new_packet) #Insert a packet into queue
				time_stamp_q.put(cur_time)
				__ready = select.select([],[client_receiver],[])
				if (should_drop(packet_drop_probability) == False) :
					print ("resent the packet number %d at time %f" %(new_packet.data_num, cur_time))
					client_receiver.send(new_packet_string)
			time.sleep(0.0025)


def pkt_receiver(resend_pkts):
	global client_sender
	global client_receiver
	global expected_pkt
	global expected_ack
	global q
	global time_stamp_q
	global timer_duration
	while(True) :
		cur_time = time.time()*1000 - base_time
		if (time_stamp_q.empty() == False) :
			if abs(cur_time - time_stamp_q.top()) >= timer_duration :
				# We should have got the acknowledgement for this packet by now
				# Means we need to signal the timeout event
				print ("Timeout occured at time %f, will need to resend all the packets in window" %cur_time)
				resend_pkts.set()
				respond_to_pck_resending(resend_pkts)

		ready = select.select([client_sender],[],[],0.005)
		if(ready[0]):
			data = client_sender.recv(4096)
			packet = pickle.loads(data)
			cur_time = time.time()*1000 - base_time
			if isinstance(packet, data_frame) :
				if packet.data_num == expected_pkt :
					print ("received data packet - %d at time %f" %(expected_pkt, cur_time))
					# create and send the acknowledgement for this received packet
					ack = ack_frame(expected_pkt)
					ack_string = pickle.dumps(ack)
					ready = select.select([],[client_receiver],[])
					print ("sending ack for data packet - %d at time %f" %(expected_pkt, cur_time))

					if (should_drop(ack_drop_probability) == False) :
						print ("Success - ack for data packet - %d at time %f" %(expected_pkt, cur_time))
						client_receiver.send(ack_string)
					expected_pkt = (expected_pkt + 1)%max_seq_num
			elif isinstance(packet, ack_frame):
				print ("received ack for data packet - %d at time %f" %(packet.ack_num, cur_time))
				# print ("**** %d $$$$" %q.size())				
				while((q.empty()==False) and ((q.top()).data_num != packet.ack_num)) :
					q.get()
					time_stamp_q.get()
				if ((q.empty()==False) and ((q.top()).data_num == packet.ack_num)) :
					q.get()
					time_stamp_q.get()
				# print ("**** %d" %q.size())


if __name__ == '__main__':
    resend_pkts = threading.Event()

    pkt_sender = threading.Thread(name='pkt_sender', 
                      target=pkt_sender,
					  args=[resend_pkts])
    pkt_sender.start()

    pkt_receiver = threading.Thread(name='pkt_receiver', 
                      target=pkt_receiver,
					  args=[resend_pkts])
    pkt_receiver.start()