from pwn import process, remote, context

# context.log_level = "debug"
# io = process(["python", "server.py"])
io = remote("edu-ctf.csie.org", 42069)

# hack for unknown socket bug...
io.send(b"0\n")
io.recvuntil(b"> ")

money = 1.2


def get_bit():
    global money
    io.sendafter(b"> ", b"1\n")
    new_money = float(io.recvlineS(timeout=1).strip())
    bit = 1 if new_money > money else 0
    money = new_money
    return bit


from sage.all import GF, companion_matrix, vector, PolynomialRing

# from sage.matrix.berlekamp_massey import berlekamp_massey
# states = [random() for _ in range(128)]
# poly = berlekamp_massey(list(map(GF(2), states)))
# print(poly)

# precomputed
P = PolynomialRing(GF(2), "x")
x = P.gen()
poly = (
    x ** 64
    + x ** 61
    + x ** 60
    + x ** 58
    + x ** 57
    + x ** 56
    + x ** 55
    + x ** 53
    + x ** 51
    + x ** 46
    + x ** 44
    + x ** 43
    + x ** 39
    + x ** 38
    + x ** 37
    + x ** 36
    + x ** 35
    + x ** 34
    + x ** 33
    + x ** 31
    + x ** 29
    + x ** 28
    + x ** 27
    + x ** 26
    + x ** 25
    + x ** 23
    + x ** 18
    + x ** 16
    + x ** 15
    + x ** 11
    + x ** 10
    + x ** 8
    + x ** 7
    + x
    + 1
)

states = [get_bit() for _ in range(64)]
M = companion_matrix(poly, "bottom")
future_states = list(M ** 64 * vector(states[-64:])) + list(
    M ** 128 * vector(states[-64:])
)  # probably enough to get money = 2.4
io.recvuntil(b"> ")
io.send("".join([str(s) + "\n" for s in future_states]).encode())
print(io.recvallS())
