from flag import flag
import random


class MyRandom:
    def __init__(self):
        self.n = 256
        self.a = random.randrange(256)
        self.b = random.randrange(256)

    def random(self):
        tmp = self.a
        self.a, self.b = self.b, (self.a * 69 + self.b * 1337) % self.n
        tmp ^= (tmp >> 3) & 0xDE
        tmp ^= (tmp << 1) & 0xAD
        tmp ^= (tmp >> 2) & 0xBE
        tmp ^= (tmp << 4) & 0xEF
        return tmp


class TruelyRandom:
    def __init__(self):
        self.r1 = MyRandom()
        self.r2 = MyRandom()
        self.r3 = MyRandom()
        print(self.r1.a, self.r1.b)
        print(self.r2.a, self.r2.b)
        print(self.r3.a, self.r3.b)

    def random(self):
        def rol(x, shift):
            shift %= 8
            return ((x << shift) ^ (x >> (8 - shift))) & 255

        o1 = rol(self.r1.random(), 87)
        o2 = rol(self.r2.random(), 6)
        o3 = rol(self.r3.random(), 3)
        o = (~o1 & o2) ^ (~o2 | o3) ^ (o1)
        o &= 255
        return o


assert len(flag) == 36

rng = TruelyRandom()
random_sequence = [rng.random() for _ in range(420)]

for i in range(len(flag)):
    random_sequence[i] ^= flag[i]

open("output.txt", "w").write(bytes(random_sequence).hex())
