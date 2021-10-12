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
    m = long_to_bytes(x)
    if b"FLAG" in m:
        print(m)
        break
