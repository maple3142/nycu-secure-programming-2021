import ipaddress


def parse_addr(s):
    addr, port = s.split(":")
    return str(
        ipaddress.IPv4Address(int.from_bytes(bytes.fromhex(addr), "little"))
    ), int(port, 16)


with open("net.txt") as f:
    for i, line in enumerate(f.readlines()):
        if i == 0:
            continue
        toks = line.strip().split()
        print(parse_addr(toks[1]), parse_addr(toks[2]))
