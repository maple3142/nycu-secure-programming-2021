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


def get_orthogonal_vecs(b):
    B = matrix(b).T.augment(matrix.identity(len(b)))
    B = B.stack(vector([M] + [0] * len(b)))
    B[:, 0] *= 2 ^ 20
    print(B.dimensions())
    for row in B.BKZ():
        if row[0] == 0:
            cf = row[1:]
            assert sum([x * y for x, y in zip(cf, b)]) % M == 0
            # print(vector(cf) * X.change_ring(Zmod(M)))
            yield vector(cf)


Xleftkernel = matrix(list(get_orthogonal_vecs(b))[:N])

# compute orthogonal basis with lattice reduction
B = Xleftkernel.T.augment(matrix.identity(L))
B[:, :N] *= 2 ^ 10
R = B.BKZ()

# basis of X in [-1,0,1]
# Xleftkernel*LX = O
LX = matrix([row[N:] for row in R if row[:N] == 0])


def is_good(v):
    if all([x == 0 for x in v]):
        return None
    if all([0 <= x <= 1 for x in v]):
        return tuple(v)
    if all([-1 <= x <= 0 for x in v]):
        return tuple(-v)


# based on https://eprint.iacr.org/2020/461.pdf Appendix D
Xvecs = []
for v in LX:
    if is_good(v):
        Xvecs.append(tuple(v))
for v in Xvecs:
    vv = vector(v)
    for u in LX:
        if (t := is_good(vv + u)) and t not in Xvecs:
            Xvecs.append(t)
        if (t := is_good(vv - u)) and t not in Xvecs:
            Xvecs.append(t)
print(len(Xvecs))

assert all([tuple(v) in list(map(tuple, X.T)) for v in Xvecs])  # sanity check
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
