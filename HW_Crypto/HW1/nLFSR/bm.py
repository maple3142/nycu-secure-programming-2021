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

from sage.matrix.berlekamp_massey import berlekamp_massey

states = [random() for _ in range(128)]
ply = berlekamp_massey(list(map(F, states)))
M = companion_matrix(ply, "bottom")
assert vector(states[-64:]) == M ** 64 * vector(states[:64])
