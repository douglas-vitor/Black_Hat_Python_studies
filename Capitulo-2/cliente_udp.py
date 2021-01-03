import socket
#Simples cliente UDP

target_host = "192.168.1.111"
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"AAABBBCCC", (target_host, target_port))

data, addr = client.recvfrom(4096)

print(data)