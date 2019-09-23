import sys
import test
import struct

class Packet:
	
	#CTOR
	#data input
	#TIPE 	(int)	{0, 1, 2, 3}
	#ID 	(int)	{0, 1, 2,..., 14, 15}
	#SEQ 	(int)	{0, 1, 2,..., 65534, 65535}
	#DATA 	(byte array) {...}

	def __init__(self, TYPE, ID, SEQ, DATA):
		self.TYPE = TYPE
		self.ID = ID
		self.SEQ = SEQ
		self.LENGTH = len(DATA)
		self.DATA = DATA

	def get_Packet(self):
		type_id = self.concat_type_ID(self.TYPE, self.ID)
		seq = self.encode_16_bits(self.SEQ)
		length = self.encode_16_bits(self.LENGTH)
		data = bytearray(self.DATA)

		#hasil concatenate
		result = type_id + seq + length + data
		# checksum
		hasil_checksum = self.checksum()
		return result[:5] + hasil_checksum + result[5:]

	#gabung type dan id, output: 1 byte
	#DEF ini DONE
	def concat_type_ID(self, type, id):
		result = ((self.TYPE << 4) | self.ID)
		return int(result).to_bytes(1, byteorder="little", signed=False)

	def encode_16_bits(self, param):
		a = struct.pack("<H", param)
		b = bytearray(a)
		return b
	
	#return encoded 16 bits
	def decode_16_bits(self, param):
		#temp = bin(int.from_bytes(param, byteorder="little", signed=False))
		#return int(temp, 2)
		temp = struct.unpack("<H", param)
		return temp[0]

	#XOR
	def checksum(self):
		type_id = self.concat_type_ID(self.TYPE, self.ID)
		seq = self.encode_16_bits(self.SEQ)
		length = self.encode_16_bits(self.LENGTH)
		data = bytearray(self.DATA)

		#hasil concatenate
		result = type_id + seq + length + data
		# jika byte ganjil, tambahkan 1 byte \x0
		if (len(result)%2 == 1):
			result += (b'\0')
		#temp = bytearray(result ^ result for (result, result) in zip(result, result))
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
		temp_SEQ = bytes_input[1]
		temp_LENGTH = bytes_input[3:5]
		temp_DATA = bytes_input[7: len(bytes_input)]

		return Packet(temp_TYPE, temp_ID, temp_SEQ, temp_DATA)
	#keluarin integer ID dari input integer konkatenasi type + id
	#DONE
	def get_ID(int_concat):
		#masking 4 bit terakhir dengan 1111
		return (int_concat & 15) 

	#keluarin integer TYPE dari input integer konkatenasi type + id
	#DONE
	def get_type(int_concat):
		#shifting ke kanan sebanyak 4 bit
		return (int_concat >> 4)

# CTOR :: <new_var> = Packet(tipe, id, seq, data)
# Prekondisi : data sudah dalam bytearray

# Karena masih kelas, belum menjadi PACKET yg sebenarnya
# panggil method ini dgn return byte packet
# <nama_obj>.get_Packet()

# Di receiver, terima packet dengan static method:

# Packet.bytesToPacket(<param>)
# Prekondisi : <param> harus dalam bentuk BYTES

# return dari method itu sebuah object Packet

# Mau cari nilai CHECKSUM dari packet, tinggal method

# <nama_obj>.checksum()


# di bawah ini contoh sm testingnya


# f_img = open("GIT.txt", "rb")
# num = f_img.read()
# f_img.close()

# P1 = Packet(1, 3, 3, (num))
# temp = P1.checksum()
# print(type(temp))
# print(len(temp))
# print(len(P1.get_Packet()))
# print(type(P1.get_Packet()))
# P_temp = P1.get_Packet()
# print("\n\n")
# P2 = Packet.bytesToPacket(P_temp)
# print(P1.TYPE, " ", P2.TYPE)
# print(P1.ID, " ", P2.ID)
# print(P1.SEQ, " ", P2.SEQ)
# print(P1.LENGTH, " ", P2.LENGTH)
# if (P1.DATA == P2.DATA and P1.checksum() == P2.checksum()):
# 	print("P1 dan P2 identik")