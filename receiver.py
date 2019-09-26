# Again we import the necessary socket python module
import socket
import time
import os
import sys
import argparse
import random
import errno
from packet import Packet 

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
    self.fd = open(folder + '/' + str(self.id), 'ab')
  
  def update_sequence(self):
    
    self.sequence += 1
  
  def is_active(self):
    return self.active
  
  def write(self, data):
    self.fd.write(data)
  
  def finalize(self):
    self.active = False
    self.fd.close()

class Client:
  # Static attributes
  client_list = []  # Client obj
  client_port_list = [] # Client port (int)

  def __init__(self, port: int):
    self.port = str(port)
    self.files = []
    self.folder = receiver_folder + '/' + self.port
    print('New client connected using port:', self.port)
    if not os.path.exists(self.folder):
      os.makedirs(self.folder)

    Client.client_port_list.append(port)
    Client.client_list.append(self)
  
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
    return (port in Client.client_port_list)
  
  @staticmethod
  def get_client(port: int): # port: int
    for client_iter in Client.client_list:
      if (int(client_iter.port) == port):
        return client_iter
    assert(False)

UDP_IP_ADDRESS = "localhost"
UDP_PORT_NO = 6789

def main():
  server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  server_sock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
  print('Receiver started on ', UDP_IP_ADDRESS, ':', UDP_PORT_NO, sep="")
  print('Your file(s) will be saved in', (receiver_folder + '/'), end="\n\n")

  while (True):
    data, addr = server_sock.recvfrom(Packet.MAX_PACKET_SIZE)

    sender_port = addr[1]

    recv_pkt = None
    try:
      recv_pkt = Packet.bytesToPacket(data)
    except:
      continue

    if (recv_pkt.CHECKSUM != recv_pkt.compute_checksum()):  # invalid data
      continue
    
    # Message type
    msg_type = recv_pkt.TYPE

    # Message id
    msg_id = recv_pkt.ID

    # Message sequence
    msg_seq = recv_pkt.SEQ
    
    # Send ACK-like packet
    ack_packet = None
    if (msg_type == Packet.DATA):
      ack_packet = Packet(Packet.ACK, msg_id, msg_seq)
    elif (msg_type == Packet.FIN):
      ack_packet = Packet(Packet.FIN_ACK, msg_id, msg_seq)
    server_sock.sendto(ack_packet.get_Packet(), addr)

    msg_data = recv_pkt.DATA
    client = {}
    if (not Client.is_connected_client(sender_port)): # new client
      client = Client(sender_port) 
    else:
      client = Client.get_client(sender_port)
    
    file_idx = client.search_file(msg_id)
    if (file_idx == -1):
      print("Receiving new file with\nPacket ID:", msg_id, "\nPort:", client.port, end="\n\n")
      file_idx = client.add_new_file(msg_id)
    file_obj = client.files[file_idx]

    if (msg_type == Packet.DATA):
      if ((file_obj.sequence+1) == msg_seq and file_obj.is_active()):
        file_obj.sequence += 1
        file_obj.write(msg_data)
    
    elif (msg_type == Packet.FIN):
      if ((file_obj.sequence+1) == msg_seq and file_obj.is_active()):
        file_obj.update_sequence()
        file_obj.write(msg_data)
        file_obj.finalize()
        print("File with\nPacket ID:", msg_id, "\nPort:", client.port, "\nSuccessfully received!", end="\n\n")
    

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Receive File(s) through UDP that simulates TCP')
  parser.add_argument('Hostname', metavar='host', type=str, help='Hostname')
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
  except KeyboardInterrupt:
    pass
  finally:
    for client in Client.client_list:
      for file_recv_obj in client.files:
        file_recv_obj.finalize()
    print("\rReceiver is exiting..")