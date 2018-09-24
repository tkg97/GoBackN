import socket

client = socket.socket()
client.connect(('10.0.2.2', 6654))

for i in range(10):
	client.send("%d"%i)
	print (client.recv(1024))

client.send("hello")
print (client.recv(1024))

client.send("hey")
print (client.recv(1024))