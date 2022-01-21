from flag import flag
import random
import string

charset = string.ascii_letters + string.digits + '_{}'

class MyRandom:
	def __init__(self):
		self.n = 2**256
		self.a = random.randrange(2**256)
		self.b = random.randrange(2**256)

	def _random(self):
		tmp = self.a
		self.a, self.b = self.b, (self.a * 69 + self.b * 1337) % self.n
		tmp ^= (tmp >> 3) & 0xde
		tmp ^= (tmp << 1) & 0xad
		tmp ^= (tmp >> 2) & 0xbe
		tmp ^= (tmp << 4) & 0xef
		return tmp

	def random(self, nbit):
		return sum((self._random() & 1) << i for i in range(nbit))

assert all(c in charset for c in flag)
assert len(flag) == 60

random_sequence = []
for i in range(6):
	rng = MyRandom()
	random_sequence += [rng.random(8) for _ in range(10)]

ciphertext = bytes([x ^ y for x, y in zip(flag.encode(), random_sequence)])
print(ciphertext.hex())

