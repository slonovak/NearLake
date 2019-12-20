import socket
client = socket.socket()
client.connect(('localhost', 7777))
client.send(input().encode())
while True:
	msg = client.recv(10)
	print(msg)