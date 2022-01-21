from Crypto.Util.number import *

plen = 256
qlen = 256


def level2():
    global p1, p2, q1, q2
    while True:
        p1 = getPrime(plen)  # 512-bit number
        p2 = (p1 + 1) // 2
        if isPrime(p2):
            break

    q1 = getPrime(qlen)
    q2 = getPrime(qlen)

    return p1 * q1, p2 * q2


n1, n2 = level2()
# n1 = p1*q1
# n2 = p2*q2
# 2*n2 = (p1+1)*q2


def lucas_v(a, n):
    # computes n-th lucas number for v_n=a*v_{n-1}-v_{n-2} with fast matrix power
    v0 = 2
    v1 = a
    R = a.base_ring()
    M = matrix(R, [[a, -1], [1, 0]])
    v = M ^ (n - 1) * vector(R, [v1, v0])
    return v[0]


# based on Williams p+1: http://users.telenet.be/janneli/jan/factorization/williams_p_plus_one.html
for a in prime_range(3, 10000):
    p = gcd(lucas_v(Mod(a, n1), 2 * n2) - 2, n1)
    if 1 < p < n1:
        break
print(p)
