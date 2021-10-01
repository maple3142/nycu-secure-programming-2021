from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# fmt: off
stream = [0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1]
iv = bytes.fromhex("cd2832f408d1d973be28b66b133a0b5f")
encrypted_flag = bytes.fromhex("1e3c272c4d9693580659218739e9adace2c5daf98062cf892cf6a9d0fc465671f8cd70a139b384836637c131217643c1")
# fmt: on


class LFSR:
    def __init__(self, key, taps):
        d = max(taps)
        assert len(key) == d, "Error: key of wrong size."
        self._s = key
        self._t = [d - t for t in taps]

    def _sum(self, L):
        s = 0
        for x in L:
            s ^= x
        return s

    def _clock(self):
        b = self._s[0]
        self._s = self._s[1:] + [self._sum(self._s[p] for p in self._t)]
        return b

    def getbit(self):
        return self._clock()


class Geffe:
    def __init__(self, key):
        assert (
            key.bit_length() <= 19 + 23 + 27
        )  # shard up 69+ bit key for 3 separate lfsrs
        key = [
            int(i) for i in list("{:069b}".format(key))
        ]  # convert int to list of bits
        self.LFSR = [
            LFSR(key[:19], [19, 18, 17, 14]),
            LFSR(key[19:46], [27, 26, 25, 22]),
            LFSR(key[46:], [23, 22, 20, 18]),
        ]

    def getbit(self):
        b = [lfsr.getbit() for lfsr in self.LFSR]
        return b[1] if b[0] else b[2]


from z3 import *


def to_bits(bv, n):
    # simplify will make it faster
    return [simplify(Extract(n - 1 - i, n - 1 - i, bv)) for i in range(n)]


key = BitVec("key", 69)
key0 = Extract(68, 68 - 19 + 1, key)
key1 = Extract(49, 49 - 27 + 1, key)
key2 = Extract(22, 22 - 23 + 1, key)
lfsr3 = [
    LFSR(to_bits(key0, 19), [19, 18, 17, 14]),
    LFSR(to_bits(key1, 27), [27, 26, 25, 22]),
    LFSR(to_bits(key2, 23), [23, 22, 20, 18]),
]


def combined_bit(ls):
    b = [lfsr.getbit() for lfsr in ls]
    return (b[0] & b[1]) | (~b[0] & b[2])


sol = Solver()

for b in stream:
    sol.add(combined_bit(lfsr3) == b)

print("solving")
if sol.check() == sat:
    m = sol.model()
    k = m.eval(key).as_long()
    key = sha1(str(k).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    print(unpad(cipher.decrypt(encrypted_flag), 16))

    k0 = m.eval(key0).as_long()
    print(f"{k0:019b}")
    k1 = m.eval(key1).as_long()
    print(f"{k1:027b}")
    k2 = m.eval(key2).as_long()
    print(f"{k2:023b}")
