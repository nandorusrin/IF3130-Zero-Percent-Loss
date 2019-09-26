import sys
import struct

class Packet:
  # Packet Size
	MAX_PACKET_DATA_SIZE = 32768
	MAX_PACKET_SIZE = MAX_PACKET_DATA_SIZE + 7
	
	# Packet type
	DATA = 0
	ACK = 1
	FIN = 2
	FIN_ACK = 3

	def __init__(self, TYPE: int, ID: int, SEQ: int, DATA=b'', CHECKSUM=0):
		self.TYPE = TYPE
		self.ID = ID
		self.SEQ = SEQ
		self.LENGTH = len(DATA)
		self.DATA = DATA
		self.CHECKSUM = CHECKSUM

	def get_Packet(self):
		type_id = self.concat_type_ID(self.TYPE, self.ID)
		seq = self.encode_16_bits(self.SEQ)
		length = self.encode_16_bits(self.LENGTH)
		data = bytearray(self.DATA)

		result = type_id + seq + length + data
		hasil_checksum = self.compute_checksum()
		return result[:5] + hasil_checksum + result[5:]

	def concat_type_ID(self, type, id):
		result = ((self.TYPE << 4) | self.ID)
		return int(result).to_bytes(1, byteorder="little", signed=False)

	def encode_16_bits(self, param):
		a = struct.pack("<H", param)
		b = bytearray(a)
		return b
	
	def decode_16_bits(self, param):
		temp = struct.unpack("<H", param)
		return temp[0]	# struct.unpack return tuple

	def compute_checksum(self):
		type_id = self.concat_type_ID(self.TYPE, self.ID)
		seq = self.encode_16_bits(self.SEQ)
		length = self.encode_16_bits(self.LENGTH)
		data = bytearray(self.DATA)

		result = type_id + seq + length + data
		if (len(result)%2 == 1):
			result += (b'\0')
		
		xor_result = bytearray(2)
		xor_result[0] = result[0]
		xor_result[1] = result[1]
		for i in range(2, len(result), 2):
			xor_result[0] ^= result[i]
			xor_result[1] ^= result[i+1]
		return xor_result

	@staticmethod
	def bytesToPacket(bytes_input):
		temp_type_id = bytearray(bytes_input)[0]
		temp_TYPE = Packet.get_type(temp_type_id)
		temp_ID = Packet.get_ID(temp_type_id)

		temp_SEQ = struct.unpack("<H", bytes_input[1:3])[0]	# struct.unpack return tuple
		temp_LENGTH = bytes_input[3:5]
		temp_CHECKSUM = bytes_input[5:7]
		temp_DATA = bytes_input[7: len(bytes_input)]

		return Packet(temp_TYPE, temp_ID, temp_SEQ, temp_DATA, temp_CHECKSUM)
	
	def get_ID(int_concat):
		# masking 4 bit terakhir dengan 1111
		return (int_concat & 15) 

	def get_type(int_concat):
		# shifting ke kanan sebanyak 4 bit
		return (int_concat >> 4)
