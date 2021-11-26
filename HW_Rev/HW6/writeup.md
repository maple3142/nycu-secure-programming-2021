# fifo

拿 ida 打開一看可以知道它會對 `/tmp/khodsmeogemgoe` 寫入一個 ELF，以及對 `/tmp/bnpkevsekfpk3/aw3movsdirnqw` 寫入一些 binary (named pipe)。然後還會使用 fork + execve 去執行 `/tmp/khodsmeogemgoe`。

可以先把 `/tmp/khodsmeogemgoe` 複製出來叫 `fifo2`。而複製 `/tmp/bnpkevsekfpk3/aw3movsdirnqw` 的時候比較麻煩，因為會發現它已經被刪掉了。
把 `fifo2` 放進 ida 可以發現就是它在 `unlink` 的刪掉的。

我的作法是先到 `/tmp/bnpkevsekfpk3` 裡面 `mkfifo aw3movsdirnqw`，然後 `cat aw3movsdirnqw > tmp`。之後再另一個 shell 中執行 `./fifo` 這樣就能在 `tmp` 這個檔案中得到需要的資料了。

另外 reverse `fifo2` 也能看到它會從 `/tmp/bnpkevsekfpk3/aw3movsdirnqw` 讀檔案，之後做一些 xor 之後直接 call 那個 `tmp` 的資料，所以可以知道 `tmp` 中是 machine code。

嘗試去 disassemble 它可以知道它裡面會用一些 syscall，和一個 loop 在那邊跑。不過其實不用看懂裡面在做什麼也能解這題。

關鍵是 `fifo2` 裡面 `sub_1209` 函數會把原本的一些 bytes 和 `tmp` 裡面的東西做一些 xor，所以直接 gdb 下斷點在適當的地方就能在 stack 上看到 flag 了。

一個做法是 `gdb ./fifo` 然後 `set follow-fork-mode child` 之後 `run`，然後會看到它卡在某個地方不會動，此時用另一個 shell 把 child process kill 掉之後就能在 stack 上看到 flag。

另一個簡單的做法是直接 `strace -f ./fifo`，然後就會看到它用 udp socket 對 `192.168.130.1` 送 flag
