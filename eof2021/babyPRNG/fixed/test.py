class MyRandom:
    def __init__(self, a, b):
        self.n = 2 ** 256
        self.a = a
        self.b = b

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


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])


keys = [
    bytes([rng.random(8) for _ in range(10)])
    for a in range(2)
    for b in range(2)
    if (rng := MyRandom(a, b))
]
ct = bytes.fromhex(
    "9dfa2c9ccd5c84c61feb00ea835e848732ac8701da32b5865a84db59b08532b6cf32ebc10384c45903bf860084d018b5d55a5cebd832ef8059ead810"
)
for i in range(0, len(ct), 10):
    for k in keys:
        s = xor(ct[i : i + 10], k)
        if s.isascii():
            print(s.decode(), end="")
print()

# FLAG{1_pr0m153_1_w1ll_n07_m4k3_my_0wn_r4nd0m_func710n_4641n}
