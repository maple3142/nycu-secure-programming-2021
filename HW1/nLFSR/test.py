import os


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


from sage.all import GF, companion_matrix, vector
from sage.matrix.berlekamp_massey import berlekamp_massey


states = [random() for _ in range(1024)]
poly = berlekamp_massey(list(map(GF(2), states)))
print(poly)
M = companion_matrix(poly, "bottom")
print(vector(states[64:128]))
print(M ** 64 * vector(states[:64]))
