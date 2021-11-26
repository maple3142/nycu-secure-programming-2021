from pwn import ELF

elf = ELF("./list")

l = 0x40A0 - 0x4020
buf1 = elf.read(0x4020, l)
buf2 = elf.read(0x40A0, l)

for i in range(0, 32 * 4, 4):
    a = int.from_bytes(buf1[i : i + 4], "little") ^ 0x5A
    b = int.from_bytes(buf2[i : i + 4], "little") ^ 0xA5
    print(chr(a ^ b), end="")
