from pwn import process, remote, context
from hashlib import md5, sha256
from ast import literal_eval
from Crypto.Util.number import bytes_to_long
from sage.matrix.matrix2 import Matrix

# context.log_level = "debug"


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
io = remote("edu-ctf.csie.org", 42074)
io.recvuntil(b"P = ")
Px, Py = literal_eval(io.recvlineS().strip())


def sign(m: bytes):
    io.sendlineafter(b"3) exit", b"1")
    io.sendlineafter(b"you?\n", m)
    r, s = literal_eval(io.recvlineS())
    h = bytes_to_long(sha256(m).digest())
    return h, r, s


h1, r1, s1 = sign(b"peko")
h2, r2, s2 = sign(b"miko")
kc = int(md5(b"secret").hexdigest() + "0" * len(md5(b"secret").hexdigest()), 16)

Z = Zmod(n)
P = PolynomialRing(Z, "k1,k2,d")
k1, k2, d = P.gens()
PP = P.remove_var(d)
f1 = s1 * (kc + k1) - (h1 + r1 * d)
f2 = s2 * (kc + k2) - (h2 + r2 * d)
f = PP(str(resultant(f1, f2, d)))

# _, a, b = (f / f.coefficients()[0]).coefficients()
# K = 2 ^ 128
# B = matrix(ZZ, [[n, 0, 0], [a, 1, 0], [b, 0, K]])
# for row in B.LLL():
#     if row[-1] == K:
#         k1, k2, _ = row
#         k1 = -k1
#         break

a, b, c = f.coefficients()
B = matrix(ZZ, [[n, 0, 0], [a, 1, 0], [b, 0, 1]])
lb = [ZZ(-c), 0, 0]
ub = [ZZ(-c), 2 ^ 128, 2 ^ 128]
load("solver.sage")
result, applied_weights, fin = solve(matrix(B), list(lb), list(ub))
_, k1, k2 = result

assert f(k1, k2) == 0, "try again"

k1 += kc
k2 += kc

G = E(Gx, Gy)
P = E(Px, Py)
assert (k1 * G).xy()[0] == r1, "try again"
assert (k2 * G).xy()[0] == r2, "try again"

d = ZZ((s1 * Z(k1) - h1) / r1)
assert d * G == P, "try again"

h = bytes_to_long(sha256(b"Kuruwa").digest())
k = 87
r = Z((k * G).xy()[0])
s = (h + r * d) / k

io.sendlineafter(b"3) exit", b"2")
io.sendlineafter(b"username: ", b"Kuruwa")
io.sendlineafter(b"r: ", str(r).encode())
io.sendlineafter(b"s: ", str(s).encode())
io.interactive()

# FLAG{adfc9b68bd6ec6dbf6b3c9ddd46aafaea06a97ee}
