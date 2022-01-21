import random
import string

charset = string.ascii_letters + string.digits + "_{}"


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


random_sequence = []
for i in range(6):
    rng = MyRandom()
    random_sequence += [rng.random(8) for _ in range(20)]
print(random_sequence)
s = set(random_sequence)

ct = bytes.fromhex(
    "9dfa2c9ccd5c84c61feb00ea835e848732ac8701da32b5865a84db59b08532b6cf32ebc10384c45903bf860084d018b5d55a5cebd832ef8059ead810"
)
flag = ""
for c in ct:
    cands = set([x for x in s if c ^ x in charset.encode()])
    if len(cands) == 1:
        flag += chr(c ^ next(iter(cands)))
    else:
        # print(cands)
        xx = [chr(c ^ x) for x in cands]
        if "_" in xx:
            flag += "_"
        elif set(xx) == set(["4", "Y"]):
            flag += "4"
        elif set(xx) == set(["X", "5"]):
            flag += "5"
        print([chr(c ^ x) for x in cands])
print(flag)

# FLAG{1_pr0m153_1_w1ll_n07_m4k3_my_0wn_r4nd0m_func710n_4641n}
