import os
from math import sin


def MyHash(s):
    A = 0x464C4147
    B = 0x7B754669
    C = 0x6E645468
    D = 0x65456173
    E = 0x74657245
    F = 0x6767217D

    def G(X, Y, Z):
        return (X ^ (~Z | ~Y) ^ Z) & 0xFFFFFFFF

    def H(X, Y):
        return (X << Y | X >> (32 - Y)) & 0xFFFFFFFF

    X = [int((0xFFFFFFFE) * sin(i)) & 0xFFFFFFFF for i in range(256)]
    for i, b in enumerate(s):
        k, l = int(b), i & 0x1F
        A = (B + H(A + G(B, C, D) + X[k], l)) & 0xFFFFFFFF
        B = (C + H(B + G(C, D, E) + X[k], l)) & 0xFFFFFFFF
        C = (D + H(C + G(D, E, F) + X[k], l)) & 0xFFFFFFFF
        D = (E + H(D + G(E, F, A) + X[k], l)) & 0xFFFFFFFF
        E = (F + H(E + G(F, A, B) + X[k], l)) & 0xFFFFFFFF
        F = (A + H(F + G(A, B, C) + X[k], l)) & 0xFFFFFFFF
    return "".join(map(lambda x: hex(x)[2:].rjust(8, "0"), [A, F, C, B, D, E]))


def pad(s: bytes, s_size=None):
    if s_size is None:
        s_size = len(s)
    s += bytes([0x80])
    if len(s) % 128 > 120:
        while len(s) % 128 != 0:
            s += bytes(1)
    while len(s) % 128 < 120:
        s += bytes(1)
    s += bytes.fromhex(hex(s_size * 8)[2:].rjust(16, "0"))
    return s


def verify(*stuff):
    print("verify")
    print(pad(b"&&".join(stuff)))
    return MyHash(pad(b"&&".join(stuff)))


def lea(h: str, ln: int, ext: bytes):
    p = pad(b"a" * ln)[ln:]
    A, F, C, B, D, E = [int(h[i : i + 8], 16) for i in range(0, len(h), 8)]
    lln = ln + len(p)
    ext = pad(ext, len(ext) + lln)

    def G(X, Y, Z):
        return (X ^ (~Z | ~Y) ^ Z) & 0xFFFFFFFF

    def H(X, Y):
        return (X << Y | X >> (32 - Y)) & 0xFFFFFFFF

    X = [int((0xFFFFFFFE) * sin(i)) & 0xFFFFFFFF for i in range(256)]
    for i, b in enumerate(ext):
        k, l = int(b), (i + lln) & 0x1F
        A = (B + H(A + G(B, C, D) + X[k], l)) & 0xFFFFFFFF
        B = (C + H(B + G(C, D, E) + X[k], l)) & 0xFFFFFFFF
        C = (D + H(C + G(D, E, F) + X[k], l)) & 0xFFFFFFFF
        D = (E + H(D + G(E, F, A) + X[k], l)) & 0xFFFFFFFF
        E = (F + H(E + G(F, A, B) + X[k], l)) & 0xFFFFFFFF
        F = (A + H(F + G(A, B, C) + X[k], l)) & 0xFFFFFFFF
    h = "".join(map(lambda x: hex(x)[2:].rjust(8, "0"), [A, F, C, B, D, E]))
    return h, p + ext


username = b"peko"
password = b"miko"
session = bytes.hex(os.urandom(10)).encode()
msg = b"&&".join([username, password, session])
h = MyHash(pad(msg))
print(pad(msg))
mac, p = lea(h, len(msg), b"&&flag")
session = session + p.split(b"&&")[0]
print(verify(username, password, *[session], b"flag"))
print(mac)
print(MyHash(msg + p))
print(msg + p)
