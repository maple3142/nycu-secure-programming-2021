from pwn import process, remote

# io = process(["python", "server.py"])
io = remote("edu-ctf.csie.org", 42070)
io.recvuntil(b"cipher = ")
cipher = bytes.fromhex(io.recvlineS().strip())
iv = cipher[:16]
ct = cipher[16:]


def oracle(iv, ct):
    c = iv + ct
    io.sendlineafter(b"cipher = ", c.hex().encode())
    return "YES" in io.recvlineS()


def cbc_oracle_block(oracle, prev, block, sz=16):
    rprev = prev[::-1]
    rpt = bytearray(sz)  # reversed plaintext
    for i in range(sz):
        for b in range(256):
            riv = bytearray(rpt)
            for j in range(i):
                pad = 0
                riv[j] = rpt[j] ^ rprev[j] ^ pad
            riv[i] = b
            if oracle(riv[::-1], block):
                last_pad = 0x80
                rpt[i] = last_pad ^ rprev[i] ^ b
                break
    return bytes(rpt[::-1])


def cbc_oracle(oracle, iv, ct, sz=16):
    blocks = [iv] + [ct[i : i + sz] for i in range(0, len(ct), sz)]
    pt = b""
    for block, prev in zip(blocks[::-1], blocks[:-1][::-1]):
        pt = cbc_oracle_block(oracle, prev, block) + pt
    return pt


print(cbc_oracle(oracle, iv, ct))
