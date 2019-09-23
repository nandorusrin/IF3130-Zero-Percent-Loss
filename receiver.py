# Again we import the necessary socket python module
import socket
import time
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

isSendingAck = False

while (True):
  if (not isSendingAck):
    data, addr = serverSock.recvfrom(1024)
    print("Message: ", data.decode())

  if (data.decode() == "Hello"):
    # send ack
    time.sleep(2) # simulate packet loss
    serverSock.sendto("ack".encode(), addr)
    isSendingAck = True