import socket

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789
Message = "Hello"

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
  clientSock.sendto(Message.encode(), (UDP_IP_ADDRESS, UDP_PORT_NO))
  clientSock.settimeout(1)

  data, attr = clientSock.recvfrom(1024)
  print("received ack:", data)

except socket.timeout:
  print("Timeout reached")
  clientSock.close()
