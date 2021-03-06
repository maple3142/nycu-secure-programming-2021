import os
from sage.all import *
from sage.matrix.berlekamp_massey import berlekamp_massey

state = int.from_bytes(os.urandom(8), "little")
poly = 0xAA0D3A677E1BE0BF


def step():
    global state
    out = state & 1
    state >>= 1
    if out:
        state ^= poly
    return out


def random():
    for _ in range(42):
        step()
    return step()


F = GF(2)
P = PolynomialRing(F, "x")
x = P.gen()

print(f"{poly:064b}")
print(sum(int(c) * x ** i for i, c in enumerate(f"{poly:064b}")) + x ** 64)
states = [random() for _ in range(128)]
print(berlekamp_massey(list(map(F, states))))
# poly = sum(int(c) * x ** i for i, c in enumerate(f"{poly:064b}")) + x ** 64
# poly = berlekamp_massey(list(map(F, states)))
# print(poly)
# M = companion_matrix(poly, "bottom")
# print(vector(states[64:128]))
# print(M ** 64 * vector(states[:64]))
# print(M ** 43)

# A = matrix(F, [states[i : i + 64] for i in range(64)]).T
# b = vector(F, states[-64:])
# v = A.solve_left(b)

A = matrix(F, [states[i : i + 64] for i in range(64)])
b = vector(F, states[-64:])
v = A.solve_right(b)

C = matrix.column([0] * 63)
C = C.augment(matrix.identity(63))
C = C.stack(v)
print(v)
print(C ** 64 * vector(states[-64:]))
print(vector([random() for _ in range(64)]))
