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


from itertools import combinations, product

# correlation attack


def brute(taps):
    KL = max(taps)
    for n_diff in range(KL):  # number of different bits
        for diffis in combinations(range(KL), n_diff):
            key_cand = stream[:KL]
            key_cand = [1 - x if i in diffis else x for i, x in enumerate(key_cand)]
            lfsr = LFSR(key_cand, taps)
            output = [lfsr.getbit() for _ in range(256)]
            same = sum(a == b for a, b in zip(stream, output))
            if same >= 180:  # more than 0.75
                return key_cand


k1 = brute([27, 26, 25, 22])
k2 = brute([23, 22, 20, 18])
print("k1", k1)
print("k2", k2)
# only partial k0 are known, need to bruteforce
k0 = [None if k1[i] == k2[i] else (1 if k1[i] == stream[i] else 0) for i in range(19)]
print("k0", k0)

unk_idxs = [i for i in range(19) if k0[i] is None]
for bs in product(range(2), repeat=len(unk_idxs)):
    for i, b in zip(unk_idxs, bs):
        k0[i] = b
    l0 = LFSR(k0, [19, 18, 17, 14])
    l1 = LFSR(k1, [27, 26, 25, 22])
    l2 = LFSR(k2, [23, 22, 20, 18])

    def getbit():
        b = [l.getbit() for l in [l0, l1, l2]]
        return b[1] if b[0] else b[2]

    output = [getbit() for _ in range(256)]
    if all(a == b for a, b in zip(output, stream)):
        print("k0", k0)
        break

k = int("".join(map(str, k0 + k1 + k2)), 2)
key = sha1(str(k).encode()).digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
print(unpad(cipher.decrypt(encrypted_flag), 16))

# could be sped up a lot with pypy3
