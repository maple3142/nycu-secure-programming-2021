import sys


def genModular(x):
    if x <= 2 * 210:
        return random_prime(2 ^ x, False, 2 ^ (x - 1))
    return random_prime(2 ^ 210, False, 2 ^ 209) * genModular(x - 210)


N, L = 100, 200
M = genModular(int(N * N * 0.07 + N * log(N, 2)))

# generate a random vector in Z_M
a = vector(ZZ, [ZZ.random_element(M) for _ in range(N)])

# generate a random 0/1 matrix
while True:
    X = Matrix(ZZ, L, N)
    for i in range(L):
        for j in range(N):
            X[i, j] = ZZ.random_element(2)
    if X.rank() == N:
        break

# let's see what will this be
b = X * a
for i in range(L):
    b[i] = mod(b[i], M)

# print('N =', N)
# print('L =', L)
# print('M =', M)
# print('b =', b)

x = vector(ZZ, int(N))
for j in range(N):
    for i in range(L):
        x[j] = x[j] * 2 + X[i, j]


def bad():
    print("They're not my values!!!")
    sys.exit(0)


def calc(va, vx):
    ret = [0] * L
    for i, vai in enumerate(va):
        for j in range(L):
            bij = (vx[i] >> (L - 1 - j)) & 1
            ret[j] = (ret[j] + vai * bij) % M
    return ret


def onevec(i):
    v = vector(ZZ, L)
    v[i] = 1
    for j in range(N, L):
        v[j] = randint(1, M)
    return v


def knapsack(a, c):
    B = matrix(ZZ, a).T.augment(matrix.identity(len(a)) * 2)
    B = B.stack(vector([-ZZ(c)] + [-1] * len(a)))
    B = B.stack(vector([M] + [0] * len(a)))
    B[:, 0] *= 2 ^ 10
    for row in B.LLL():
        if (
            row[0] == 0
            and not all([x == 0 for x in row])
            and all([-1 <= x <= 1 for x in row])
        ):
            v = vector([(x + 1) // 2 for x in row][1:])
            print("probably")
            # print(row[1:])
            # print(v)
            # print(B.solve_left(row))
            if sum([x * y for x, y in zip(v, a)]) % M == c % M:
                print("good")
                return v


# def to_binvec(x, bits=M.nbits()):
#     return vector(ZZ, map(int, f'{x:0{bits}b}'))

# print(M.nbits())
# print([x.nbits() for x in b])
# B=matrix([to_binvec(x) for x in b] + [to_binvec(M)])
# for row in B.echelon_form():
#     print(row)


# def knapsack(a, c):
#     B = matrix(ZZ, a).T.augment(matrix.identity(len(a)))
#     B = B.stack(vector([-ZZ(c)] + [0] * len(a)))
#     B = B.stack(vector([ZZ(M)] + [0] * len(a)))
#     B[:, 0] *= 2 ^ 10
#     B = B.change_ring(ZZ)
#     for row in B.LLL():
#         # print(row)
#         # print(B.solve_left(row))
#         if (
#             row[0] == 0
#             and not all([x == 0 for x in row])
#             and all([0 <= x <= 1 for x in row])
#         ):
#             v = vector(row[1:])
#             print("good")
#             print(row[1:])
#             print(v)
#             print(B.solve_left(row))
#             assert sum([x * y for x, y in zip(v, a)]) % M == c % M
#             return v


def diffseq(xs):
    return [x - y for x, y in zip(xs, xs[1:])]


def difftill(xs, k=N):
    while len(xs) > k:
        # print(xs)
        xs = diffseq(xs)
    return xs


# print("b0")
# print(knapsack(a, b[0]))
# print(knapsack(difftill(b, N), b[0]))
# print("b1")
# print(knapsack(a, b[1]))
# print(knapsack(difftill(b, N), b[1]))


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
            print(sum([x * y for x, y in zip(cf, b)]) % M == 0)
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
            print(row, row[N:] in X.T)
print(len(goodvecs))

# for v in goodvecs:
#     tt = X.solve_right(v)
#     print([x for x in tt if x != 0])

for v in X.T:
    tt = matrix(goodvecs).solve_left(v)
    # print([x for x in tt if x != 0])
    print([(i, x) for i, x in enumerate(tt) if x != 0])

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
assert all([tuple(v) in list(map(tuple, X.T)) for v in Xvecs])
XX = matrix(ZZ, Xvecs).T
aa = XX.change_ring(Zmod(M)).solve_right(vector(b)).change_ring(ZZ)


xx = vector(ZZ, int(N))
for j in range(N):
    for i in range(L):
        xx[j] = xx[j] * 2 + XX[i, j]

x = vector(ZZ, int(N))
for j in range(N):
    for i in range(L):
        x[j] = x[j] * 2 + X[i, j]

print(calc(aa, xx) == calc(a, x))
