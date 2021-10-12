# nLFSR

這題的雖然說是 LFSR，但是看它的 `step` 函數並不像一般預期中 LFSR 的模樣。這個去 Wiki 查一下可以看到它屬於 [Galois LFSR](https://en.wikipedia.org/wiki/Linear-feedback_shift_register#Galois_LFSRs)，characteristic polynomial 是一般 Fibonacci LFSR 的 Reciprocal polynomial。

針對 `step` 可以用這個方法去得到 companion matrix:

```python
F = GF(2)
P = PolynomialRing(F, "x")
x = P.gen()


states = [step() for _ in range(128)]
ply = sum(int(c) * x ** i for i, c in enumerate(f"{poly:064b}")) + x ** 64
M = companion_matrix(ply, "bottom")
assert vector(states[-64]) == M ** 64 * vector(states[:64])
```

不過我們要預測的 `random` 函數是 `step` 的 output，固定跳過 43 個 states 出來的結果。在 Wiki 上有一句:

> One can obtain any other period by adding to an LFSR that has a longer period some logic that shortens the sequence by skipping some states.

這代表就算是 `random`，它的輸出也是個 LFSR，但是這次我們不知道它的 characteristic polynomial ，這邊有兩個做法可以處裡。第一個方法是利用 [Berlekamp–Massey algorithm](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm) 可以透過給予 128 個 states，然後它就會找出這個 LFSR 的多項式:

```python
F = GF(2)
P = PolynomialRing(F, "x")
x = P.gen()

from sage.matrix.berlekamp_massey import berlekamp_massey

states = [random() for _ in range(128)]
ply = berlekamp_massey(list(map(F, states)))
M = companion_matrix(ply, "bottom")
assert vector(states[-64:]) == M ** 64 * vector(states[:64])
```

另一個方法是注意到在一般 LFSR (`step`) 的情況下，$s_{64} = (s_0, s_1, \cdots, s_{63}) \cdot \vec{v}$，其中的 $\vec{v}$ 就是 companion matrix $C$ 的 last row，這個 $v$ 同時也符合 $s_{i+64} = (s_i, s_{i+1}, \cdots, s_{i+63}) \cdot \vec{v}$。

既然 `random` 的輸出 $r_i=s_{43i}$，根據 Wiki 所述它也是個 LFSR，這樣代表對於 $r_i$ 這個 sequence 也存在一個 companion matrix $C'$，它的 last row 是 $\vec{v}'$。既然 $r_{i+64} = (r_i, r_{i+1}, \cdots, r_{i+63}) \cdot \vec{v}'$，我們可以寫出這個線性系統:

$$
\begin{bmatrix}
r_0 & r_1 & \cdots & r_{63} \\
r_1 & r_2 & \cdots & r_{64} \\
\vdots & \vdots & \vdots & \vdots \\
r_{63} & r_{64} & \cdots & r_{126}
\end{bmatrix}
\vec{v}' =
\begin{bmatrix}
r_{64} \\
r_{65} \\
\vdots \\
r_{127}
\end{bmatrix}
$$

只需要 128 個 states $r_i$ 就能求出我們所需要的 $\vec{v}'$，之後就能用 $\vec{v'}$ 重新構造回 $C'$，一樣就能預測未來的輸出了。

> 如果在內積的部分把 $\vec{v}'$ 寫到左側，那一樣能寫出一個 $xA=b$ 的線性系統來解。

```python
F = GF(2)
P = PolynomialRing(F, "x")
x = P.gen()

states = [random() for _ in range(128)]

A = matrix(F, [states[i : i + 64] for i in range(64)])
b = vector(F, states[-64:])
v = A.solve_right(b)

# Or you can solve it in xA = b
# A = matrix(F, [states[i : i + 64] for i in range(64)]).T
# b = vector(F, states[-64:])
# v = A.solve_left(b)

C = matrix.column([0] * 63)
C = C.augment(matrix.identity(63))
C = C.stack(v)
print(v)
assert C ** 64 * vector(states[:64]) == vector(states[-64:])
assert C ** 64 * vector(states[-64:]) == vector([random() for _ in range(64)])
```

無論用哪個方法，我們都已經有辦法預測 `random` 函數的 output 了。至於在原本的題目中要取得 states 的方法也不難，只要一直先猜同一個數字例如 `1`，只要錢增加就代表它輸出的是 `1`，減少的話就代表輸出的是 `0`。

有個可能會遇到的問題是使用上述的兩個方法都起碼要 128 個 states，但是在原本的題目中根據那個金錢數量是很難撐到讓你拿完 128 個 states 的。不過很快就會發現說一個 LFSR 的 characteristic polynomial 和 companion matrix 都和 states 無關，並不會產生變化。

所以可以先預先把它計算出來，然後解題的腳本只需要取得 64 個 states 就能用矩陣去 predict 未來的輸出了，完整的腳本附在 `nLFSR/solve.py` 中。

# Single

這題的橢圓曲線只給了 $p$，$a, b$ 都是未知的。但是它有給你三個點 $G, A, B$，只要拿任兩個點列出以下的方程式就能解出 $a, b$ 了:

$$
\begin{aligned}
y_1^2 &\equiv x_1^3 + ax_1 + b \pmod{p} \\
y_2^2 &\equiv x_2^3 + ax_2 + b \pmod{p}
\end{aligned}
$$

解出 $a, b$ 之後用 Sage 的 `EllipticCurve` 試著產生 `EllipticCurve(GF(p), [a, b])` 會失敗，check 一下會發現 $4a^3+27b^2 \equiv 0 \pmod{p}$，所以是條 Singular curve。

嘗試把 $x^3 + ax + b$ 分解看看會發現它是屬於 $(x-\alpha)^2(x-\beta)$ 的形式，所以這個是 Node。定義

$$
\varphi(P(x, y)) = \frac{y+\sqrt{\alpha-\beta}(x-\alpha)}{y-\sqrt{\alpha-\beta}(x-\alpha)}
$$

之後因為 $\varphi$ 是個從 $\mathbb{E}(\mathbb{F}_p)$ 到 $\mathbb{F}_p$ 的 group homomorphism，即 $\varphi(P+Q)=\varphi(P) \cdot \varphi(Q)$，所以 $\varphi(A)=\varphi(d_AG)=\varphi(G)^{d_A}$。

試著分解 $p-1$ 可以發現它是相當 smooth 的，所以直接利用 Pohlig-Hellman 在 $\mathbb{F}_p$ 上解 dlog 後就能獲得 $d_A$。

之後只要計算 $S=d_AB$ 之後就能算出 key 去把 flag 解密了，不過因為 Sage 沒辦法支援在這種 Singular curve 上運算，所以直接用原先題目腳本所提供的改一改就可以計算了。

前面第一部分到算出 $d_A$ 的 code 在 `solve1.sage`，然後最後計算 $S$ 和解密 flag 的部分在 `solve2.py` 之中。
