# Again we import the necessary socket python module
import socket
import time
import os
import sys
import argparse
import random
import errno
import packet

class PACKET_TYPE:
  DATA = 0
  ACK = 1
  FIN = 2
  FIN_ACK = 3

receiver_folder = ''
class ReceivingFile:
  def __init__(self, folder, file_id):
    self.id = file_id
    self.sequence = -1
    self.active = True
    self.fd = open(folder + '/' + self.id, 'ab')
  
  def update_sequence(self, new_seq):
    self.sequence = new_seq
  
  def is_active(self):
    return self.active
  
  def write(self, data):
    self.fd.write(data)
  
  def finalize(self):
    self.active = False
    self.fd.close()

class Client:
  client_list = []

  def __init__(self, port): # port: int
    self.port = str(port)
    self.files = []
    self.folder = receiver_folder + '/' + self.port
    if not os.path.exists(self.folder):
      os.makedirs(self.folder)

    Client.client_list.append(self.port)
  
  def __eq__(self, other):
    if isinstance(other, Client):
      return self.port == other.port
    return False
  
  def search_file(self, file_id):
    for i in range(len(self.files)):
      if (self.files[i].id == file_id):
        return i
    return -1
  
  def add_new_file(self, file_id):
    self.files.append(ReceivingFile(self.folder, file_id))
    return len(self.files)-1
  
  @staticmethod
  def is_connected_client(port):  # port: int
    return (port in Client.client_list)
  
  @staticmethod
  def get_client(port): # port: int
    for client_iter in Client.client_list:
      if (client_iter.port == str(port)):
        return client_iter
    assert(False)

UDP_IP_ADDRESS = "localhost"
UDP_PORT_NO = 6789

connected_client = []

def main():
  print('Receiver started')
  server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  server_sock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

  while (True):
    data, addr = server_sock.recvfrom(65507)

    # send ack
    # time.sleep(2) # simulate packet loss
    server_sock.sendto("ack".encode(), addr)

    sender_port = addr[1]

    print("Message size received: ", len(data))
    
    # dummy
    # message type
    msg_type = int.from_bytes(data[:1], byteorder='little', signed=False)
    print('message type:', msg_type)

    # message id
    msg_id = str(int.from_bytes(data[1:2], byteorder='little', signed=False))
    print('message id:', msg_id)

    # message sequence
    msg_seq = int.from_bytes(data[2:3], byteorder='little', signed=False)
    print('message sequence:', msg_seq)

    msg_data = bytearray(data)[3:]


    client = {}

    if (not Client.is_connected_client(sender_port)): # new client
      client = Client(sender_port)  # create new client
      connected_client.append(client)
    else:
      client = Client.get_client(sender_port)
    
    file_idx = client.search_file(msg_id)
    if (file_idx == -1):
      file_idx = client.add_new_file(msg_id)
    file_obj = client.files[file_idx]

    if (msg_type == PACKET_TYPE.DATA):
      if (file_obj.sequence != msg_seq and file_obj.is_active()):
        file_obj.update_sequence(msg_seq)
        file_obj.write(msg_data)
    
    elif (msg_type == PACKET_TYPE.FIN):
      if (file_obj.sequence != msg_seq and file_obj.is_active()):
        file_obj.update_sequence(msg_seq)
        file_obj.write(msg_data)
        file_obj.finalize()
    

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Receive File(s) through UDP that simulates TCP')
  parser.add_argument('Hostname', metavar='host', type=str, help='UDP Hostname')
  parser.add_argument('Port', metavar='port', type=int, help='UDP port')
  parser.add_argument('Folder', metavar='folder', type=str, help='Received Folder', default='receiver')
  
  args = parser.parse_args()
  UDP_IP_ADDRESS = args.Hostname
  UDP_PORT_NO = args.Port
  receiver_folder = args.Folder
  if not os.path.exists(receiver_folder):
    try:
      os.mkdir(receiver_folder)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise

  try:
    main()
  finally:
    for client in connected_client:
      for file_recv_obj in client.files:
        file_recv_obj.finalize()
