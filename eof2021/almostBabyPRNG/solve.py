class MyRandom:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def random(self):
        tmp = self.a
        self.a, self.b = self.b, (self.a * 69 + self.b * 1337) & 0xFF
        tmp ^= (tmp >> 3) & 0xDE
        tmp ^= (tmp << 1) & 0xAD
        tmp ^= (tmp >> 2) & 0xBE
        tmp ^= (tmp << 4) & 0xEF
        return tmp


def rol(x, shift):
    shift %= 8
    return ((x << shift) ^ (x >> (8 - shift))) & 255


ct = list(
    bytes.fromhex(
        "d5de8acdc0fa83d9c5bbe683cb33ef07949d6faeee8b00f6a2cc10cad800ca818e1cfd34f96f8fe71c9dbb3930ec8fb89183c9eef059cddcdc62a3fcf96eaea6dcab1bde96db8dbb13e3eb5d144fec9c6c91637cffdb0d8c988c2a189a8aaeaa136afe8cd469dddedf88ed7effbf2fd89e8f8afa88beb9ba1150eaaec0c8fdb5d4fbe3efff8ca866ecbf2bda996a7f9e136d6d6e1afbccb664e24d5ef98e9fa63e8d8b3a385aef999389d9dcfbe9f8f6d4908bdaf9bdbd8dfeaebafea28aca8c9181cb8ca8cbc9a6f48893dcf94b8b4efca91a8ab1a84f9893ac4fafb86ee9dbff7a9949ff6e8fe40a9daa2c30ea99b89383c9ecf459d8d8dc66a1fcff6daeb4caab0ad896c88cbb11e3eb4c134ff9886c84617cf9cf0d8b9d8c3b189a88adaa117dfe8ac369c8c9df88f87ef9ad2fce9f8f9be988a9adba1343eabbd6c8e8b4d4eaf2eff989a865febf3acb996c6d9e11696d6c1afbd9b664e64b5eff899fb42c8d9a383849ea99918dd9cdf8e9ede6d4858ddaffadbd8affaeabfaa288cd8c9392cb8abbcbdcb5f48882dcff5d8b58f9a90b9db1bf5f9891bb4fbaaa6efcdeff6b8c49"
    )
)


def gen_table(shift, ln=128):
    table = {}

    for a in range(256):
        for b in range(256):
            r = MyRandom(a, b)
            stream = tuple([rol(r.random(), shift) for _ in range(ln)])
            table[stream] = (a, b)
    return table


def solve_gen1():
    # a == ~(((~a)&b)^((~b)|c)^a) for 75%
    table = gen_table(87)
    for stream, (a, b) in table.items():
        same = [0] * 8
        for i in range(36, len(stream)):
            for j in range(8):
                mask = 1 << j
                if ((~ct[i]) & mask) == stream[i] & mask:
                    same[j] += 1
        rates = [s / (len(stream) - 36) for s in same]
        if sum(rates) / len(rates) > 0.70:
            print(a, b, rates)
            return a, b, stream


def solve_gen3():
    # c == ~(((~a)&b)^((~b)|c)^a) for 75%
    table = gen_table(3)
    for stream, (a, b) in table.items():
        same = [0] * 8
        for i in range(36, len(stream)):
            for j in range(8):
                mask = 1 << j
                if ((~ct[i]) & mask) == stream[i] & mask:
                    same[j] += 1
        rates = [s / (len(stream) - 36) for s in same]
        if sum(rates) / len(rates) > 0.70:
            print(a, b, rates)
            return a, b, stream


a1, b1, s1 = solve_gen1()
a3, b3, s3 = solve_gen3()
table2 = gen_table(6)
for s2, (a2, b2) in table2.items():
    oo = [((~o1 & o2) ^ (~o2 | o3) ^ (o1)) & 0xFF for o1, o2, o3 in zip(s1, s2, s3)]
    if oo[36:] == ct[36 : len(oo)]:
        print(a2, b2)
        print(bytes([x ^ y for x, y in zip(oo, ct)][:36]))

# pypy3 takes less than 3s
# FLAG{1_l13d_4nd_m4d3_4_n3w_prn6_qwq}
