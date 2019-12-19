import socket
client = socket.socket()
client.connect(('localhost', 7777))
client.settimeout(0.005)
while True:
	client.send(bytes(input().encode()))
	try:
		msg = client.recv(1024)
		print(msg)
	except socket.timeout:
		pass