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
import logging
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
timer_duration = 1000 #in milliseconds

q = Queue(transmit_window)
time_stamp_q = Queue(transmit_window)
tempq = Queue(transmit_window)

packet_drop_probability = 0.1
ack_drop_probability = 0.05

def should_drop(threshold) :
	temp = random.uniform(0,1)
	if(temp<=threshold) : return True
	else : return False

client_receiver_address = ('169.254.224.230', 6654)

receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = '169.254.224.230'
port = 6653
address = (ip, port)
receiver.bind(address)
receiver.setblocking(0)

logfile_name = "host1.log"

logging.basicConfig(filename=logfile_name, level=logging.DEBUG)

base_time = time.time()*1000

def send(new_packet_string):
	global receiver
	while(True) :
		try:
			receiver.sendto(new_packet_string, client_receiver_address)
			return
		except Exception as __e:
			pass

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
	global max_seq_num
	while(True):
		if(resend_pkts.is_set()) : continue
		cur_time = time.time()*1000 - base_time
		if(q.full() == False):
			if (tempq.empty()) :
				# create and send packet here
				new_packet = data_frame(frame_to_send % max_seq_num)
				cur_time = time.time()*1000 - base_time

				logging.info ("generated packet %d, at time %f" %(frame_to_send, cur_time))

				new_packet_string = pickle.dumps(new_packet)
				q.put(new_packet) #Insert a packet into queue
				time_stamp_q.put(cur_time)
				if (should_drop(packet_drop_probability) == False) :
					logging.info ("packet %d, at time %f, sent successfully" %(frame_to_send, cur_time))
					send(new_packet_string)
				frame_to_send = (frame_to_send + 1)%max_seq_num
			else :
				#Get that pack from tempq top
				new_packet = tempq.get()
				cur_time = time.time()*1000	- base_time				
				
				logging.info ("Trying to resend the packet number %d at time %f" %(new_packet.data_num, cur_time))

				new_packet_string = pickle.dumps(new_packet)
				q.put(new_packet) #Insert a packet into queue
				time_stamp_q.put(cur_time)
				if (should_drop(packet_drop_probability) == False) :
					logging.info ("resent the packet number %d at time %f" %(new_packet.data_num, cur_time))
					send(new_packet_string)
			time.sleep(0.002)


def pkt_receiver(resend_pkts):
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
				logging.info ("Timeout occured at time %f, will need to resend all the packets in window" %cur_time)
				resend_pkts.set()
				respond_to_pck_resending(resend_pkts)

		ready = select.select([receiver],[],[],0.005)
		if(ready[0]):
			try:
				data, __address = receiver.recvfrom(4096)
				packet = pickle.loads(data)
				cur_time = time.time()*1000 - base_time
				if isinstance(packet, data_frame) :
					if packet.data_num == expected_pkt :
						logging.info ("received data packet - %d at time %f" %(expected_pkt, cur_time))
						# create and send the acknowledgement for this received packet
						ack = ack_frame(expected_pkt)
						ack_string = pickle.dumps(ack)
						logging.info ("sending ack for data packet - %d at time %f" %(expected_pkt, cur_time))

						if (should_drop(ack_drop_probability) == False) :
							logging.info ("Success - ack for data packet - %d at time %f" %(expected_pkt, cur_time))
							send(ack_string)
						expected_pkt = (expected_pkt + 1)%max_seq_num
				elif isinstance(packet, ack_frame):
					logging.info ("received ack for data packet - %d at time %f" %(packet.ack_num, cur_time))			
					while((q.empty()==False) and ((q.top()).data_num != packet.ack_num)) :
						q.get()
						time_stamp_q.get()
					if ((q.empty()==False) and ((q.top()).data_num == packet.ack_num)) :
						q.get()
						time_stamp_q.get()
			except Exception as __e:
				pass


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