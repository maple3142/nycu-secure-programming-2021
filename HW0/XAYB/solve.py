data = b"\xb4\xbe\xb3\xb5\x89\xa5\xc2\x9d\xad\xa5\xb3\xa5\xad\xab\xc2\xa7\xad\xc7\xc2\xad\xbe\x84\x91\xb9\x8b\xad\x85\x93\x86\x91\x9a\xad\x84\xad\xad\xbe\xb0\xa4\xc6\xcb\xa6\xa2\xb0\xb7\x95\x8f\x00\x00"
print(bytes(x ^ 0xF2 for x in data))
