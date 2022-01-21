from Crypto.Util.number import *
import os

from flag import flag

blen = 256

def rsa(p: int, q: int, message: bytes):
	n = p * q
	e = 65537
	
	pad_length = n.bit_length() // 8 - len(message) - 2 # I padded too much
	message += os.urandom(pad_length)
	m = bytes_to_long(message)
	return (n, pow(m, e, n))

def level1(message1: bytes, message2: bytes):
	while True:
		p1 = getPrime(blen) # 512-bit number
		p2 = (p1 - 1) // 2
		if isPrime(p2):
			break

	q1 = getPrime(blen)
	q2 = getPrime(blen)

	return rsa(p1, q1, message1), rsa(p2, q2, message2)

def level2(message1: bytes, message2: bytes):
	while True:
		p1 = getPrime(blen) # 512-bit number
		p2 = (p1 + 1) // 2
		if isPrime(p2):
			break

	q1 = getPrime(blen)
	q2 = getPrime(blen)

	return rsa(p1, q1, message1), rsa(p2, q2, message2)

assert len(flag) == 44
l = len(flag) // 4
m1, m2, m3, m4 = [flag[i * l: i * l + l] for i in range(4)]
c1, c2 = level1(m1, m2)
c3, c4 = level2(m3, m4)

print(f'{c1 = }')
print(f'{c2 = }')
print(f'{c3 = }')
print(f'{c4 = }')
