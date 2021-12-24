# final

這題的小服務漏洞相當的多，試著用了一個和 `final.py` 稍微不同的做法自己解了一遍。

題目的 struct 如下，`malloc` 的 chunk size 為 `0x30`:

```c++
typedef struct _Animal {
    char type[0x10];
    unsigned long len;
    char *name;
    void (*bark)(char *, char *);
} Animal;
```

首先是要先 leak heap address，我用的方法是先想辦法弄兩個 `name` 為 `0x20` 的 chunk 分別再 free，可以讓 tcache 0x20 填上兩個 chunk。之後弄一個 animal 的 name 大小不為 `0x20` 之後再塞個防止 consolidate 的 animal，然後利用 `change` 的部分將長度改為 `0` 就可以把用 `malloc(0)` 得到 `0x20` 的 chunk，由於 `read(0, buf, 0)` 無作用所以就拿到了一個 uninitialized buffer，從上面讀 name 就能從 `fd` 拿到 heap address。

接下來用 UAF 讓一個 animal 的 name 指向另一個 animal 的 chunk，就可以改到 `name` pointer，由此可以任意讀寫。中途可以插一個 unsorted bin 就能讓 libc address 出現在 heap 上，利用任意讀寫就可以 leak libc 後寫 `system` 到 `__free_hook` 之後再 `free("/bin/sh")` 拿到 shell。這部分和 easyheap 也相同。

詳見 `final/solve.py`

# easyheap

這題提供了一個簡單的小服務可以讓你新增、刪除和編輯書籍等地功能，其中的 Book struct 如下:

```c++
typedef struct _Book {
    char *name;
    unsigned long index;
    unsigned long price;
    unsigned long namelen;
} Book;
```

其中的 `name` 是在新增新的書籍時可以自己決定長度，然後會用那個長度去 `malloc` 一塊 buffer 回來。

最主要的漏洞在於 `delete_book` 函數中 `free` 之後沒把書真正的給刪除，還是能夠編輯和讀取書籍，這樣就有 UAF 的問題:

```c++
    free(books[idx]->name);
    free(books[idx]);
```

雖然在編輯書籍的時候輸入名稱的長度一律是 `0x20`，有 heap buffer overflow 的問題，不過我的解法沒用到這個。

找到的一個簡單解法是說新增兩本書 `0` 和 `1` 之後把他們 free 掉，中間可以隨便多新增一本書防止 consolidation。可以控制 `1` 的 `fd` 指到 `0` 的 buffer 上，這樣在編輯 `1` 的 `name` 的時候就會改到 `0` 的 `*name` pointer，由此就能得到任意記憶體讀寫。

另外是在 UAF 的情況可以很容易的直接讀出 heap address。

至於要 RCE 還需要有 libc，一個簡單的方法是把其中一個的 `name` 設到超過 tcache 範圍，例如 `0x430 + 0x10` 被 free 之後會直接進 unsortedbin，而 unsortedbin 的頭尾都會有 chunk 的 `fd` 或是 `bk` 指回 `main_arena` 由此可以拿到 libc address。而 heap 上的相對位置會是固定的，所以只要有個 heap address 就能利用任意讀拿到 libc address。

有 libc address 和任意讀寫之後就簡單了，用 offset 算 `system` 和 `__free_hook` 的位置，然後把 `system` 寫到 `__free_hook` 之後讓它 `free` 一個有 `/bin/sh` 的 chunk 就有 shell 了。

詳見 `easyheap/solve.py`

Flag: `FLAG{to_easy...}`

# beeftalk

這題有個需要註冊/登入之後可以聊天的服務，登入之後也有編輯自身資訊的功能。其中 User struct 如下:

```c++
typedef struct _User {
    char *name;
    char *desc;
    char *job;
    char *pipe_name;
    char *fifo0;
    char *fifo1;
    unsigned long namelen;
    unsigned long token;
    long int assets;
} User;
```

其中 `malloc(sizeof(User))` 本身會拿到 `0x50` 的 chunk，而 `desc` 在建立的時候也是 `malloc(0x40)` 產生的，所以大小也是 `0x50`。

這題一樣有個明顯的 UAF 在 `free_user` 那邊，`free` 掉之後沒清 pointer。而因為 `token` 是在 chunk 比較後面的地方，只要該 chunk 還沒被 reuse 的情況下就還能登入，然後一樣可以讀取自身的名字和修改 `name`, `desc` 等等。

這題會遇到的一個小問題是 `User` 的 chunk 本身是和 `desc` 同大小的，分別以 `user0`, `desc0` 的情況下去表示 chunk 的話，註冊兩個 user 然後刪掉兩個 user 之後會 heap 的狀況大致如下:

```
tcache 0x50: user1 -> desc1 -> user0 -> desc0
```

沒辦法和 `easyheap` 一樣直接去修改 pointer。

不過有個技巧是利用 tcache 大小只有 7 個的這個特性，註冊四個 user 然後刪掉四個 user 之後會是如下:

```
tcache 0x50: desc3 -> user2 -> desc2 -> user1 -> desc1 -> user0 -> desc0
fastbin 0x50: user3
```

此時如果再建立一個 user 的話會有 `user4 == desc3` 和 `desc4 == user2`，此時如果修改 `desc4` 就能改到 `user2` 的 `*name` pointer，達成任意讀寫。

因為 heap address 在 UAF 的情況一樣是隨便拿都有，所以目標一樣是想辦法從 unsorted bin leak libc。只是這次沒辦法自己決定 malloc 大小的情況下比較麻煩。我主要是利用到 `signup` 函數中如果發現讀取進來的 username 長度超過 `0x20` 就會 `realloc(tmpuser->name, nr)`。因為 `realloc` 在新申請的大小超過原本大小的情況下行為大致上就是 `free` 之後 `malloc`，所以只要讓 `nr` (讀進來的字元數)超過 fastbin 大小，然後也讓它的數量超過 tcache 的 7 個限制後 chunk 就會進到 unsorted bin。

之後就一樣用固定的 offset 和 heap address 去得到 libc address，之後一樣對 `__free_hook` 寫 `system` 得到 shell，這部分和 `easyheap` 幾乎相同。

詳見 `beeftalk/solve.py`

Flag: `FLAG{beeeeeeOwO}`
