from pwn import *
import ast

L = 200
N = 100

io = remote("eof.ototot.cf", 51820)
io.recvuntil(b"M = ")
M = ZZ(int(io.recvlineS().strip()))
io.recvuntil(b"b = ")
b = ast.literal_eval(io.recvlineS().strip())


def knapsack2(b):
    B = matrix(b).T.augment(matrix.identity(len(b)))
    # B = B.stack(vector([0] + [-1] * len(b)))
    B = B.stack(vector([M] + [0] * len(b)))
    B[:, 0] *= 2 ^ 20
    # print(B.change_ring(Zmod(10)))
    print(B.dimensions())
    for row in B.BKZ():
        # print(row)
        if row[0] == 0:
            cf = row[1:]
            # print(sum([x * y for x, y in zip(cf, b)]) % M == 0)
            # print(vector(cf) * X.change_ring(Zmod(M)))
            yield vector(cf)


p_vecs = list(knapsack2(b))
Xleftkernel = matrix(p_vecs[:N])

B = Xleftkernel.T.augment(matrix.identity(L))
B[:, :N] *= 2 ^ 10
R = B.BKZ()

goodvecs = []
for row in R:
    if row[0] != 0:
        print("??")
        continue
    if all(-1 <= x <= 1 for x in row):
        if any(x < 0 for x in row):
            row = -row
        assert Xleftkernel * row[N:] == 0
        goodvecs.append(row[N:])
        if all(0 <= x <= 1 for x in row):
            print(row)
print(len(goodvecs))

# for v in goodvecs:
#     tt = X.solve_right(v)
#     print([x for x in tt if x != 0])

# for v in X.T:
#     tt = matrix(goodvecs).solve_left(v)
#     # print([x for x in tt if x != 0])
#     print([(i, x) for i, x in enumerate(tt) if x != 0])

from itertools import product
from tqdm import tqdm

Xvecs = set()
for v in goodvecs:
    if all(0 <= x <= 1 for x in v):
        Xvecs.add(tuple(v))
        bestvec = v
print(len(Xvecs))
for v1 in tqdm(goodvecs):
    for v2 in goodvecs:
        for coef in product([-1, 0, 1], repeat=3):
            vv = coef[0] * v1 + coef[1] * v2 + coef[2] * bestvec
            if any([x < 0 for x in vv]):
                vv = -vv
            if all([0 <= x <= 1 for x in vv]) and sum(vv) != 0:
                Xvecs.add(tuple(vv))
    if len(Xvecs) == N:
        break
Xvecs = list(Xvecs)
# assert all([tuple(v) in list(map(tuple, X.T)) for v in Xvecs])
XX = matrix(ZZ, Xvecs).T
aa = XX.change_ring(Zmod(M)).solve_right(vector(b)).change_ring(ZZ)


xx = vector(ZZ, int(N))
for j in range(N):
    for i in range(L):
        xx[j] = xx[j] * 2 + XX[i, j]


def calc(va, vx):
    ret = [0] * L
    for i, vai in enumerate(va):
        for j in range(L):
            bij = (vx[i] >> (L - 1 - j)) & 1
            ret[j] = (ret[j] + vai * bij) % M
    return ret


assert tuple(calc(aa, xx)) == tuple(b)
io.sendlineafter(b"a?", " ".join(map(str, aa)).encode())
io.sendlineafter(b"x?", " ".join(map(str, xx)).encode())
io.interactive()

# FLAG{W0W_You_knoW_h0w_to_solve_H1dden_Sub5et_5um_Probl3m}
