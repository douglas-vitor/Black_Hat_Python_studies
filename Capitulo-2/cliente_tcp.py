import socket
#Simples cliente TCP

target_host = "127.0.0.1"
target_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))
header = b"GET / HTTP/1.1\r\nHOST: 127.0.0.1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\n\r\n"

client.send(header)

response = client.recv(4096)

print(response)