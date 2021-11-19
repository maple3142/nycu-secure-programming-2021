from hashlib import sha256

def proofofwork(prefix):
    i = 0
    while True:
        hashed = sha256((prefix+str(i)).encode()).hexdigest()
        if hashed.startswith('000000'):
            return i, hashed
        i += 1

if __name__ == '__main__':
    prefix = input("Prefix: ")
    ans, hashed = proofofwork(prefix)
    print("Hash:", hashed)
    print("PoW_INPUT =", ans)
