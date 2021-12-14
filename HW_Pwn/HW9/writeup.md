# sandbox

binary 保護是 nx canary pie 和 relro 都全開的。

這題題目會讀取 shellcode，長度限制 0x200，之後經過一些 filter 後執行 shellcode。filter 的部份主要做了幾件事:

* mmap 一塊新的 `rw-` 空間作為新的 `stack`，在 shellcode 前面插入 `mov rsp, stack` 和 `mov rbp, stack`
* 遇到 `syscall` 的時候使用 `jmp_func` replace 成一個呼叫 `syscall_monitor` 的 code，裡面只允許你 `exit`
* 遇到 `call reg` 的時候也用 `jmp_func` replace 成一個呼叫 `call_reg_monitor` 的 code，作用是輸出一個 `Disallow !!` 的字串

執行前還會把所有的 register 清零之後再執行 shellcode。

實作 `jmp_func` 的部份是使用 `mov r8, func_addr; call r8` 的形式達成的。`mov r8, func_addr` 的 machine code 其實就有 `func_addr` 的 little endian 的值，所以從 rip 附近去讀取就能拿到程式本身的 address，然後從 GOT table 中又能找到 libc 的 address，之後拿到 shell 的方法就很多了，我用的是 libc 中的 one gadget 就可以了。

shellcode 大致如下:

```x86asm
call rax # will be replaced by filter
mov rax, [rip-18] # rax = call_reg_monitor
add rax, 0x2c06 # rax = write@got
mov rax, [rax] # rax = write
sub rax, 0x1111d0 # rax = libc
add rax, 0xe6c84 # rax = one gadget
xor rsi, rsi # satisify one gadget condition
xor rdx, rdx # satisify one gadget condition
jmp rax # this is not call rax
```

> 一些神奇的 offset 部份是直接用 gdb 算的，用其他工具應該也能拿到

詳見 `sandbox/solve.py`

# fullchain

binary 保護除了 relro 是 partial 以外都是全開的，所以 GOT table 可寫。

程式部分就是先設置 seccomp，允許的 syscall 列表如下:

* exit_group
* exit
* close
* open
* read
* write
* mprotect
* brk
* mmap

之後進入 `chal` 函數，根據 `cnt` 變數可以讓你執行 3 次操作，每次可以先選擇一個 addr:

* global: bss 段的一塊空間，長度 `0x10`
* local: 區域變數，長度 `0x10`

之後再選擇操作:

* set: 對 addr 去 `memset`，內容可以自由決定，長度限制在 `0x10`
* read: `scanf("%24s", addr)`
* write: `printf(addr)`

`chal` 函數本身離開迴圈之後是輸出訊息後 `exit` 的，而他裡面判斷你的選擇的時候是用 `scanf("%10s", local)` 讀取輸入的，之後 `strncmp` 去比對，如果都沒比對到的話就 `exit`。

顯然有個 format string 的洞，但是 read 之後 write 一來一回就要耗掉兩次機會，這題也不是一次 format string 就能解掉的題目，所以找其他辦法。第一件可以注意到的是在選擇操作時可以輸入 `write%p` 之類的觸發 format string，雖然長度不夠寫入但是足夠 leak 出 program / stack / libc 等等的的位置了。

我這邊是選擇 leak stack (`local` 變數)的位置，由此可知 `cnt` 的位置。之後就用 read 寫入 `padding + p64(cnt_addr)` 到 `local` 去，之後第三次可以輸入 `local` 和 `write%16$n`，這樣就能把 `cnt` 變數寫入成 `5` 繼續執行。

此時可以寫出用 read global + write global 觸發長度 24 的 format string 的函數，然後可以由此又能任意 read write 任意 address 的位置，只是一次操作都會消耗三次 `cnt`。不過既然現在有 `5` 次，可以直接對 `cnt` 寫入把他改大到幾乎用不完的程度即可。

目前有任意讀寫，但是還控制不了 `rip`，由於 `chal` 函數沒有 `ret` 所以沒辦法直接 ROP。我的作法是在程式本身找到 `pop r13; pop r14; pop r15; ret` 這個 gadget (register 不重要，關鍵是 `pop pop pop ret`)，還有 libc 中有個 `pop rsp; ret` 結合起來 stack pivoting。

當 GOT 中的 `exit` 被改成了 `pop pop pop ret` 的時候 `call exit` 之後會先把原本的 return address `pop` 掉，之後的兩個 `pop` 是為了把 stack 上其他的移除，讓 `ret` 的時候正好是 stack 上的 `local` 的位置。因為 `local` 是可控的，可以在適當的地方寫入 `pop rsp; ret`，這樣可以控制 `rsp` 後 `ret`，也就是可以 pivot 到其他地方 ROP。

新的 stack 就在 bss 上隨便選一塊即可，內容就類似 LAB 的 Rop2win 一樣用 ROP 去 orw 即可。path 一樣是自己在 bss 上找另一塊去寫入處裡，最後就能這樣讀出 flag 了。

> 在寫入 ROP chain 的時候有踩到一個坑是 `scanf` 會在空白或是換行字元的時候 truncate，所以寫入的 address 如果正好包含那些字元可能要重新 run 一遍，但是在寫 ROP chain 的時候就要改成選好 pivot 過去的 stack address 了，不然選 `00` 結尾的 address 寫到 `09` 的時候一定會炸

詳見: `fullchain/solve.py`

# fullchain-nerf

前一題的簡單版，沒有 stack canary 且 `chal` 函數結束的地方有 `ret`，而 `myread` 改用了 `read` 去讀取，最高可以讀到 0x60 bytes。

這次 `local` overflow 可以直接蓋掉 `cnt` 得到無限次輸入，之後用 format string 可以從 stack 上找到 program address，也能任意讀寫，這樣就能從 GOT 中拿到 libc address。因為有 seccomp 所以只能用 ROP 去 ORW，需要空間夠大的 ROP chain，所以 overflow `local` 的時候要 stack pivot 才行。

用任意寫在 bss 寫入目標 path `/home/fullchain-nerf/flag` 之後可以構造 ORW 的 rop chain (一樣是和 Rop2win)，libc 裡面有一堆 gadget 能用。把 rop chain 寫到 bss 的另一塊 `newstack` 之後把 rbp 蓋成 `newstack - 8`，`ret` 蓋成任意的 `leave ; ret` 的位置，之後一樣用 overflow 把 `cnt` 改 `0` 之後就能脫離迴圈，然後 return 時 stack pivot 到 `newstack` 上，用 rop chain 去 orw 輸出 flag。

詳見: `fullchain-nerf/solve.py`
