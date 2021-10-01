import random
import json
import functools as fn
import numpy as np
import string
import hashlib

charset = string.ascii_lowercase + string.digits + ",. "
charset_idmap = {e: i for i, e in enumerate(charset)}

ksz = 80


def decrypt(ctx, key):
    N, ksz = len(charset), len(key)
    return "".join(charset[(c - key[i % ksz]) % N] for i, c in enumerate(ctx))


def toPrintable(data):
    ul = ord("_")
    data = bytes(c if 32 <= c < 127 else ul for c in data)
    return data.decode("ascii")


with open("./output.txt") as f:
    ctx = f.readline().strip()[4:]
    enc = bytes.fromhex(f.readline().strip()[6:])
ctx = [charset_idmap[c] for c in ctx]

with open("./ngrams.json") as f:
    ngrams = json.load(f)


@fn.lru_cache(10000)
def get_trigram(x):
    x = "".join(x)
    y = ngrams.get(x)
    if y is not None:
        return y
    ys = []
    a, b = ngrams.get(x[:2]), ngrams.get(x[2:])
    if a is not None and b is not None:
        ys.append(a + b)
    a, b = ngrams.get(x[:1]), ngrams.get(x[1:])
    if a is not None and b is not None:
        ys.append(a + b)
    if len(ys):
        return max(ys)
    if any(c not in ngrams for c in x):
        return -25
    return sum(map(ngrams.get, x))


@fn.lru_cache(10000)
def fitness(a):
    plain = decrypt(ctx, a)
    tgs = zip(plain, plain[1:], plain[2:])
    score = sum(get_trigram(tg) for tg in tgs)
    return score


def initialize(size):
    population = []
    for i in range(size):
        key = tuple(random.randrange(len(charset)) for _ in range(ksz))
        population.append(key)
    return population


def crossover(a, b, prob):
    r = list(a)
    for i in range(len(r)):
        if random.random() < prob:
            r[i] = b[i]
    return tuple(r)


def mutate(a):
    r = list(a)
    i = random.randrange(len(a))
    r[i] = random.randrange(len(charset))
    return tuple(r)


# known plaintext
# make it easier to converge to the correct one
ngrams["gim"] = 0
ngrams["iml"] = 0
ngrams["mli"] = 0
ngrams["oad"] = 0
ngrams["ran"] = 0
ngrams["gra"] = 0
ngrams["aph"] = 0
ngrams["sys"] = 0
ngrams["cry"] = 0
ngrams["pto"] = 0
ngrams["aut"] = 0
ngrams["hen"] = 0

keys = np.array(initialize(7000))

for i in range(400):
    fitnesses = np.array([fitness(tuple(k)) for k in keys])
    idx = fitnesses.argsort()[::-1][:500]

    best_i = idx[0]
    print(i, fitnesses[best_i], decrypt(ctx, keys[best_i]), list(keys[best_i]))

    good_keys = keys[idx]
    l = len(good_keys) // 2
    next_gen = [crossover(a, b, 0.5) for a, b in zip(good_keys[:l], good_keys[l:])]
    mutated = [mutate(k) for k in next_gen]
    keys = np.concatenate((keys[idx], np.array(mutated)))

key = keys[best_i]
k = hashlib.sha512("".join(charset[k] for k in key).encode("ascii")).digest()
print(bytes(ci ^ ki for ci, ki in zip(enc, k)))

# key = [24, 23, 30, 21, 12, 11, 12, 33, 9, 15, 37, 25, 20, 17, 36, 1, 26, 31, 35, 17, 20, 7, 2, 22, 15, 28, 25, 8, 4, 31, 29, 21, 25, 24, 19, 14, 32, 19, 16, 34, 27, 0, 28, 8, 21, 24, 21, 10, 21, 28, 4, 2, 6, 32, 20, 33, 11, 10, 36, 34, 31, 30, 28, 12, 10, 2, 19, 27, 38, 7, 0, 20, 29, 38, 27, 2, 21, 17, 1, 28]
# gimli is a 384 bits permutation designed to achieve high security with high performance across a broad range of platforms. it is currently in round 2 of the nist lightweight cryptographic project, the submission consisting of an authenticated encryption and a cryptographic hash function. in this paper, we focus on the gimli cipher, which performs authenticated encryption with associated data.
# FLAG{3c7166f852e3eaed71c81875e0c290562eff2c0}
