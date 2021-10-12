from Crypto.Util.number import *
from gmpy2 import powmod


def keygen(b):
    p = getPrime(b)
    q = getPrime(b)
    n = p * q
    e = 65537
    d = inverse(e, (p - 1) * (q - 1))
    return n, e, d


n, e, d = keygen(512)
# m = getRandomRange(1, n)
m = 4876348763
c = powmod(m, e, n)


def base3(x):
    ar = []
    while x:
        ar.append(x % 3)
        x //= 3
    return "".join(map(str, ar[::-1]))


print(m)
print(base3(m))


def oracle(x):
    # powmod is faster than pow
    return powmod(x, d, n) % 3


def crack(c, n, e, oracle):
    a = pow(3, -1, n)
    cm3 = pow(a, e, n)
    bits = [oracle(c)]
    while True:
        c = (c * cm3) % n
        r = oracle(c)
        k = sum((pow(a, i + 1, n) * b) % n for i, b in enumerate(bits[::-1])) % n
        bits.append((r - k) % 3)
        yield int("".join(map(str, bits[::-1])), 3)


for x in crack(c, n, e, oracle):
    print(x, base3(x))
    if x == m:
        print(m)
        break
