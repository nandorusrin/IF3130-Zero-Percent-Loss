import sys
import test
import struct

#gabung type dan id, output: 1 byte
#DEF ini DONE
def concat_type_ID(type, id):
	result = ((type << 4) | id)
	return int(result).to_bytes(1, byteorder="little", signed=False)

#keluarin integer ID dari input byte
def get_ID(byte):
	temp = bin(int.from_bytes(byte, byteorder="little", signed=False))
	return int(temp[-4:])
#keluarin integer TYPE dari input byte
def get_type(byte):
	return int(byte[0:-4], 2)

#encode length ke bytes
#DEF ini done
def encode_length(length):
	return length.to_bytes(2, byteorder="little", signed=False)
	

message = "hello, world!"

f_img = open("stark.jpg", "rb")
num = list(f_img.read())
print(len(num))
f_img.close()

eg = concat_type_ID(6, 4)
print(int.from_bytes(eg, byteorder="little", signed=False))
print(get_ID(eg))