import random


def tamper(x):
    x ^= (x >> 3) & 0xDE
    x ^= (x << 1) & 0xAD
    x ^= (x >> 2) & 0xBE
    x ^= (x << 4) & 0xEF
    return x


for i in range(8):
    print(f"{i:08b}", f"{tamper(i):08b}")

print(f"{0b00000011:08b} {tamper(0b00000011):08b}")


class MyRandom:
    def __init__(self):
        self.n = 2 ** 256
        self.a = random.randrange(2 ** 255) * 2 + 1
        self.b = random.randrange(2 ** 255) * 2 + 1

    def _random(self):
        tmp = self.a
        self.a, self.b = self.b, (self.a * 69 + self.b * 1337) % self.n
        tmp ^= (tmp >> 3) & 0xDE
        tmp ^= (tmp << 1) & 0xAD
        tmp ^= (tmp >> 2) & 0xBE
        tmp ^= (tmp << 4) & 0xEF
        return tmp

    def random(self, nbit):
        return sum((self._random() & 1) << i for i in range(nbit))


rng = MyRandom()
for _ in range(32):
    print(rng._random() & 1)
