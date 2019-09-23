import socket
import argparse
import os
import math

MAX_PACKET_DATA_SIZE = 65500  # to be able to comply with IP size
MAX_PACKET_SEQUENCE = 65535
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

def main():
  n_file = len(files_to_be_send)
  file_send_bool = [False for i in range(n_file)]
  file_sequence_tracker = [0 for i in range(n_file)]
  files_max_sequence = [(math.ceil(size / MAX_PACKET_DATA_SIZE)-1) for size in files_to_be_send_size] # 0..n

  client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  total = 0

  i = 0
  while (True):
    if all(file_send_bool):
      break
    
    print('i:', i)
    if (file_send_bool[i]):
      i += 1
      if (i >= n_file):
        i = 0
      continue;
    
    file_obj = files_to_be_send[i]
    last_offset = file_obj.tell()
    message = file_obj.read(MAX_PACKET_DATA_SIZE)

    try:
      print('tell', last_offset)
      print('message size:', len(message))
      client_sock.sendto(message, (UDP_IP_ADDRESS, UDP_PORT_NO))
      client_sock.settimeout(1)

      data, attr = client_sock.recvfrom(7) # ack worth 7 bytes

      print("received ack:", data)

    except socket.timeout:
      print("Timeout reached")
      file_obj.seek(last_offset)
      i += 1
      if (i >= n_file):
        i = 0
      continue;

    total += len(message)

    file_sequence_tracker[i] += 1
    print('file_sequence_tracker', file_sequence_tracker)
    if (file_sequence_tracker[i] > files_max_sequence[i]):
      file_send_bool[i] = True
    
    i += 1
    if (i >= n_file):
      i = 0

  print('total', total, files_to_be_send_size)
  client_sock.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Send File(s) through UDP that simulates TCP')
  parser.add_argument('Hostname', metavar='host', type=str, help='UDP Hostname')
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
