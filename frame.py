import random, string
class data_frame:
	def __init__(self, num):
		self.data_num = num
		self.L = random.randint(64, 256)
		self.header = "0" * 32
		self.check_sum = "0"*4
		self.data = random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(L-32)])

class ack_frame:
	def __init__(self, num):
		self.ack_num = num
		self.L = 32
		self.header = "0" * 32
		self.check_sum = "0"*4
		
