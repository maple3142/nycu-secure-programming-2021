from Crypto.Util.number import *
from gmpy2 import powmod
from pwn import process, remote

# io = process(["python", "server.py"])
io = remote("edu-ctf.csie.org", 42071)
io.recvuntil(b"n = ")
n = int(io.recvlineS().strip())
io.recvuntil(b"c = ")
c = int(io.recvlineS().strip())
e = 65537


def oracle(c):
    io.sendline(str(c).encode())
    io.recvuntil(b"m % 3 = ")
    return int(io.recvlineS().strip())


def crack(c, n, e, oracle, lim=10000):
    c0 = c
    c3 = pow(3, e, n)
    l, r = 0, n
    while r - l > lim:
        # Due to rounding problem, it can't really get an accurate answer...
        m1 = (2 * l + r) // 3
        m2 = (l + 2 * r) // 3
        c = (c3 * c) % n
        o = oracle(c)
        if o == 0:
            r = m1
        elif o == (-n) % 3:
            l = m1
            r = m2
        else:
            l = m2
    for x in range(l, r + 1):
        if powmod(x, e, n) == c0:
            return x


print(long_to_bytes(crack(c, n, e, oracle)))
