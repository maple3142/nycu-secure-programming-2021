import os
from sage.all import *

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


states = [step() for _ in range(128)]
ply = sum(int(c) * x ** i for i, c in enumerate(f"{poly:064b}")) + x ** 64
M = companion_matrix(ply, "bottom")
assert vector(states[-64:]) == M ** 64 * vector(states[:64])
