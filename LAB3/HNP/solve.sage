from pwn import process, remote
from hashlib import sha256
from ast import literal_eval
from Crypto.Util.number import bytes_to_long
from sage.matrix.matrix2 import Matrix


def resultant(f1, f2, var):
    return Matrix.determinant(f1.sylvester_matrix(f2, var))


p = 2 ^ 256 - 2 ^ 32 - 977
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
E = EllipticCurve(GF(p), [a, b])
n = E.order()

# io = process(["python", "server.py"])
# Px, Py = list(map(int, io.recvlineS().strip().split()))

io = remote("edu-ctf.csie.org", 42072)
io.recvuntil(b"P = ")
Px, Py = literal_eval(io.recvlineS().strip())


def sign(m: bytes):
    io.sendlineafter(b"3) exit", b"1")
    io.sendlineafter(b"you?\n", m)
    io.recvuntil(b"sig = ")
    r, s = literal_eval(io.recvlineS())
    h = bytes_to_long(sha256(m).digest())
    return h, r, s


h1, r1, s1 = sign(b"peko")
h2, r2, s2 = sign(b"miko")

Z = Zmod(n)
P = PolynomialRing(Z, "k1,d")
k1, d = P.gens()
f1 = s1 * k1 - (h1 + r1 * d)
f2 = s2 * (1337 * k1) - (h2 + r2 * d)
f = resultant(f1, f2, k1).univariate_polynomial()
d = ZZ(f.roots()[0][0])

G = E(Gx, Gy)
P = E(Px, Py)
assert d * G == P
h = bytes_to_long(sha256(b"Kuruwa").digest())
k = 87
r = Z((k * G).xy()[0])
s = (h + r * d) / k

io.sendlineafter(b"3) exit", b"2")
io.sendlineafter(b"username: ", b"Kuruwa")
io.sendlineafter(b"r: ", str(r).encode())
io.sendlineafter(b"s: ", str(s).encode())
io.interactive()
