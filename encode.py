import sys
import test
import struct

#gabung type dan id, output: 1 byte
#DEF ini DONE
def concat_type_ID(type, id):
	result = ((type << 4) | id)
	return int(result).to_bytes(1, byteorder="little", signed=False)

#keluarin integer ID dari input byte
#DONE
def get_ID(byte):
	temp = bin(int.from_bytes(byte, byteorder="little", signed=False))
	return int("0b"+temp[-4:], 2)

#keluarin integer TYPE dari input byte
#DONE
def get_type(byte):
	temp = bin(int.from_bytes(byte, byteorder="little", signed=False))

	return int(temp[0:-4], 2)

#encode length ke bytes
#DEF ini done
def encode_length(length):
	return length.to_bytes(2, byteorder="little", signed=False)

f_img = open("stark.jpg", "rb")
num = list(f_img.read())
print(len(num))
f_img.close()


#CONTOH
tipe = 3
ID = 5
LENGTH = 4239
eg = concat_type_ID(tipe, ID)
print("Ukuran concatenate   : ", len(eg), " byte")
print(get_type(eg))
print(get_ID(eg))
print("Hasil encode LENGTH  : ", encode_length(LENGTH))
print("Ukuran encode LENGTH : ", len(encode_length(LENGTH)), " byte(s)")