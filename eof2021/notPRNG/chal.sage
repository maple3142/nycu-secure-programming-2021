from secret import flag
import sys

def genModular(x):
    if x <= 2 * 210:
        return random_prime(2^x, False, 2^(x - 1))
    return random_prime(2^210, False, 2^209) * genModular(x - 210)

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

print('N =', N)
print('L =', L)
print('M =', M)
print('b =', b)

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


if __name__ == '__main__':
    print('What are my original values?')
    print('a?')
    aa = list(map(int, input().split()))
    print('x?')
    xx = list(map(int, input().split()))

    if len(aa) != len(a):
        bad()
    if len(xx) != len(x):
        bad()
    if calc(a, x) != calc(aa, xx):
        bad()

    print(flag)
