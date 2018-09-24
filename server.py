import socket
 
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