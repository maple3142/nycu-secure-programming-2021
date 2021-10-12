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

states = [random() for _ in range(128)]

A = matrix(F, [states[i : i + 64] for i in range(64)])
b = vector(F, states[-64:])
v = A.solve_right(b)

# Or you can solve it in xA=b
# A = matrix(F, [states[i : i + 64] for i in range(64)]).T
# b = vector(F, states[-64:])
# v = A.solve_left(b)

C = matrix.column([0] * 63)
C = C.augment(matrix.identity(63))
C = C.stack(v)
print(v)
assert C ** 64 * vector(states[:64]) == vector(states[-64:])
assert C ** 64 * vector(states[-64:]) == vector([random() for _ in range(64)])
