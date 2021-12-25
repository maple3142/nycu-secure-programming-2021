# filenote

這題很類似 LAB 的 **FILE note - (R)**，會先在 heap 上給你一個 chunk 可以寫，還有 heap buffer overflow。之後可以選擇性的開啟一個 `FILE` 並且呼叫 `fwrite(note_buf, 1, BUF_SIZE, fp);`。只是原題有提供 heap 的 address，目標只是要想辦法讀到在 heap 上的 flag。而這題沒給 address，也沒有後門，需要直接拿 shell。

因為 `_IO_FILE_plus` 是在 buffer 後 `malloc` 的，所以用 overflow 顯然可以蓋到裡面的內容。首先因為目前 `fp` 的 `fileno` 是 `3`，輸出都不會輸出的畫面上，所以可以先 overflow 把 `fileno` 改 `1` (stdout)，其中各種 `read` `write` 的 pointer 就都蓋成 0 就可以了。蓋完之後輸入一次 `3` 呼叫 `fwrite` 之後可以看到那些 pointer 又回來了，因為對於 libc 來說只是遇到還沒初始化過的 `FILE` 而已。

下個目標是要想辦法 leak 出一個 address 出來，由於不知道任何 heap address 所以沒辦法用 LAB 的做法用 `fwrite` 去 leak。(`write_base` ~ `write_ptr` 的做法)

不過仔細觀察可以看到目前的 `write_base` 都是 heap address 了，用 partial overwrite 說不定能有一些效果。例如在 `_flags` 後面只給三個 0 把 `read_ptr` `read_end` 和 `read_base` 蓋掉，之後利用 `gets` 會把字串 null terminated 的性質可以蓋到 `read_end` 的最後一個 byte。此時去從 `_IO_new_file_xsputn` 開始 trace 可以知道他會進 `_IO_new_file_overflow`，裡面如果是 unbuffered 的話可以直接 `_IO_do_write (f, f->_IO_write_base, f->_IO_write_ptr - f->_IO_write_base)`，然後可以追蹤到 `new_do_write`。目前為止和簡報中的都一樣。

在 `new_do_write` 中因為前面用 partial overwrite 的緣故，使得 `fp->_IO_read_end != fp->_IO_write_base` 成立，裡面又會遇到一些麻煩的 seek 沒辦法讓它呼叫 `sys_write`。只是注意一下可以看到函數開頭還有個 `fp->_flags & _IO_IS_APPENDING` 的檢查，如果符合的話可以跳過前面 `read_end` 相關的檢查，實際測試也真的能輸出資料到 stdout 上，裡面也很幸運的讓我們獲得了 libc 的 address。對照位置可以知道那個是 `vtable` 的指針，所以指到 libc 中是很正常的一件事。

得到 libc 之後下一步是要想辦法做寫入，可以回到 `_IO_new_file_xsputn` 那邊看，裡面在 fill buffer 的地方會呼叫 `f->_IO_write_ptr = __mempcpy (f->_IO_write_ptr, s, count);`，其中 `count` 在非 line buffering 模式是由 `count = f->_IO_write_end - f->_IO_write_ptr;` 所控制的，而 `s` 就是 `fwrite` 傳進來的 `data`。顯然只要控制 `_IO_write_ptr` 和 `_IO_write_end` 就能對一段 memory 做寫入，而內容來源就是來自本來就可以控制的那個 chunk。

寫入時選擇很多，一個簡單的做法就是對 `vtable` 所指向的 libc 中的那個位置寫入一堆 one gadget 就可以了，只是我把找到的 one gadget 都嘗試過後都不成功，只能另尋方法。

回到 `_IO_new_file_overflow` 可以看到如果當前有 `_IO_IN_BACKUP` 的 flag 的話會呼叫 `_IO_free_backup_area (f);`，往底下可以追到 `libio/genops.c` 中的 `_IO_free_backup_area`，裡面如果有 `_IO_IN_BACKUP` (必定的)的話又會先呼叫 `_IO_switch_to_main_get_area (fp);` 之後再 `free (fp->_IO_save_base);`。其中的 `_IO_switch_to_main_get_area` 大致上就只把 `read_end` 和 `save_end` 交換，還有把 `read_base` 和 `save_base` 做交換，之後 `fp->_IO_read_ptr = fp->_IO_read_base;`。因此只要在 `read_base` 寫入一個 address 並把 flags 加上 `_IO_IN_BACKUP` 的話就能讓他對指定 address 去 `free`。

所以就先在 `__free_hook` 的地方寫 `system`，然後在 `read_base` 中寫入 libc 中的 `/bin/sh` 字串的位置，之後下次 `fwrite` 只要觸發 overflow 就能 `free("/bin/sh")` 拿到 shell。測試後也能在 local 使用成功 pwntools 得到 shell。

詳見 `filenote/solve.py`

不過當我嘗試直接把 exploit 跑在 remote 的時候都會失敗，詳細來說是在 partial overwrite 之後輸入 `3` 觸發 `fwrite` 之後的地方卡住。在 local 只要 overwrite 之後輸入一次 `3` 就能拿到 libc，但是在 remote 時不知為何都只能看到 menu 而已。後來隨便測試了一些東西發現說在 remote 需要 partial overwrite 之後重複輸入 **8** 次 `3` 觸發 **8** 次 `fwrite` 後才能得到 libc，而其他部分的 exploit 都不用改就能成功。

這個的原因後來發現是在於 remote 使用的是 xinetd，把 stdin 和 stdout 導到 tcp socket 上。而 pwntools 預設的 `process` 根據官方文件可以看到他預設會開啟 tty，而 libc 似乎在單純的 pipe 模式和 tty 模式下在 buffer 大小上有些差別而導致了這個問題。在 pwntools 要模擬 pipe 模式的話可以加個 `stdout=PIPE` 給 `process`。

下面這個是一個可以看出 tty 和單純 pipe 模式下不同的小程式: (By @Kia)

```c++
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

int main() {
    struct stat buf;
    fstat(1, &buf);
    printf("%d", buf.st_blksize);
}
```
