from pwn import *

# context.log_level = "debug"
io = remote("edu-ctf.zoolab.org", 30208)


def recvchunk(type):
    io.recvuntil(type + b" *")
    name = io.recvn(1).decode()
    io.recvuntil(b"malloc(")
    size = int(io.recvuntil(b")")[:-1], 16)
    size -= 8
    pad = -size % 16
    return name, size + pad + 0x10


def recvfree():
    io.recvuntil(b"free(")
    return io.recvuntil(b")")[:-1].decode()


def solve_tcache(chks, frees):
    heap = {}
    for name, size in chks:
        heap[name] = size
    tcache = {}
    for name in frees:
        size = heap[name]
        if not size in tcache:
            tcache[size] = []
        tcache[size].append(name)
        heap.pop(name)
    s = " --> ".join(tcache.get(0x30, [])[::-1] + ["NULL"])
    io.sendlineafter(b"0x30: ?", s.encode())
    s = " --> ".join(tcache.get(0x40, [])[::-1] + ["NULL"])
    io.sendlineafter(b"0x40: ?", s.encode())


def solve_addr(chks):
    offset = {}
    cnt = 0
    for name, size in chks:
        offset[name] = cnt
        cnt += size
    io.recvuntil(b"assert( ")
    name = io.recvn(1).decode()
    io.recvuntil(b" == ")
    addr = int(io.recvuntil(b" ")[:-1], 16)
    base = addr - offset[name]
    offset = {k: base + v for k, v in offset.items()}
    io.recvuntil(b");\n")
    name = io.recvn(1).decode()
    io.sendline(hex(offset[name]).encode())


def solve_index_and_tcache_fd():
    x, x_size = recvchunk(b"unsigned long")
    y, y_size = recvchunk(b"unsigned long")
    io.recvuntil(b"Y[")
    yidx = int(io.recvn(1).decode())
    sz = 8  # unsigned long
    xidx = (x_size - 0x10 + 0x10 + sz * yidx) // sz
    io.sendline(str(xidx).encode())

    io.recvuntil(b"assert( Y == ")
    addr = int(io.recvuntil(b" ")[:-1], 16)
    io.sendlineafter(b"> ", hex(addr - x_size).encode())


def solve_fastbin_fd():
    io.recvuntil(b"malloc(")
    size = int(io.recvuntil(b")")[:-1], 16) + 0x10
    io.recvuntil(b"assert( Y == ")
    addr = int(io.recvuntil(b" ")[:-1], 16)
    io.sendlineafter(b"> ", hex(addr - size - 0x10).encode())


chks = [recvchunk(b"char") for _ in range(7)]
frees = [recvfree() for _ in range(7)]
solve_tcache(chks, frees)
solve_addr(chks)
solve_index_and_tcache_fd()
solve_fastbin_fd()
print(io.recvallS().strip())

# FLAG{heap_is_so_fun}
