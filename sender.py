import socket
import argparse
import os
import math
from packet import Packet

# IP size: 65535
# IP payload: 65535 - 20 = 65515
# UDP size: 65515
# UDP payload: 65515 - 8 = 65507
# user-defined-packet header = 7 bytes
# user-defined-packet MAX_PACKET_DATA_SIZE: 65507 - 7 = 65500 bytes

UDP_IP_ADDRESS = "localhost"
UDP_PORT_NO = 6789
files_to_be_send = []
files_to_be_send_size = []

def printProgressBar(file_names, iteration, total):
  progress_str = ""
  for i in range(0, len(file_names), 1):
    percent = ("{0:.1f}").format(100 * ((iteration[i]) / float(total[i]+1)))
    progress_str += ('[{}: {}%], '.format(file_names[i].name, percent))
  
  progress_str = '\r' + progress_str + '\r'

  print(progress_str, end='\r')

def main():
  n_file = len(files_to_be_send)
  file_sent_bool = [False for i in range(n_file)]
  file_sequence_tracker = [0 for i in range(n_file)]
  files_max_sequence = [(math.ceil(size / Packet.MAX_PACKET_DATA_SIZE)-1) for size in files_to_be_send_size] # 0..n

  client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  total = 0

  i = 0
  while (True):
    if all(file_sent_bool):
      break
    
    if (file_sent_bool[i]):
      i += 1
      if (i >= n_file):
        i = 0
      continue;
    
    file_obj = files_to_be_send[i]
    last_offset = file_obj.tell()
    pkt_dat = bytearray(file_obj.read(Packet.MAX_PACKET_DATA_SIZE))

    pkt_id = i
    pkt_type = (Packet.FIN if (file_sequence_tracker[i] == files_max_sequence[i]) else Packet.DATA)
    pkt_seq = file_sequence_tracker[i]
    pkt = Packet(pkt_type, pkt_id, pkt_seq, pkt_dat)

    recv_pkt = None
    try:
      client_sock.sendto(bytes(pkt.get_Packet()), (UDP_IP_ADDRESS, UDP_PORT_NO))
      client_sock.settimeout(5) # set timeout for 5 second

      data, addr = client_sock.recvfrom(Packet.MAX_PACKET_SIZE)

      recv_pkt = Packet.bytesToPacket(data)
      if not (recv_pkt.CHECKSUM == recv_pkt.compute_checksum()):
        file_obj.seek(last_offset)
        i += 1
        if (i >= n_file):
          i = 0
        continue
      
    except socket.timeout:
      file_obj.seek(last_offset)
      i += 1
      if (i >= n_file):
        i = 0
      continue;

    total += len(pkt.DATA)

    recv_file_id = recv_pkt.ID
    if (recv_pkt.SEQ != file_sequence_tracker[recv_file_id]):
      file_obj.seek(last_offset)
      i += 1
      if (i >= n_file):
        i = 0
      continue

    file_sequence_tracker[recv_file_id] += 1
    printProgressBar(files_to_be_send, file_sequence_tracker, files_max_sequence)
    
    if (file_sequence_tracker[recv_file_id] > files_max_sequence[recv_file_id]):
      file_sent_bool[recv_file_id] = True
    
    i += 1
    if (i >= n_file):
      i = 0

  print(len(files_to_be_send), 'File(s) sent:', [file.name for file in files_to_be_send])
  client_sock.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Send File(s) through UDP that simulates TCP')
  parser.add_argument('Hostname', metavar='host', type=str, help='Hostname')
  parser.add_argument('Port', metavar='port', type=int, help='UDP port')
  parser.add_argument('File', metavar='file(s)', type=str, nargs='+', help='Files to be send')
  
  args = parser.parse_args()
  UDP_IP_ADDRESS = args.Hostname
  UDP_PORT_NO = args.Port
  files_string = args.File

  for file in files_string:
    if not os.path.isfile(file):
      parser.error("The file %s does not exist!" % file)
      exit()
    files_to_be_send_size.append(os.path.getsize(file))
    files_to_be_send.append(open(file, "rb"))

  try:
    main()
  finally:
    for file_obj in files_to_be_send:
      file_obj.close()