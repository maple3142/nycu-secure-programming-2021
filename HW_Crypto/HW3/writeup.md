# HNP-revenge

這題是 ECDSA 的題目，題目允許你 sign 任意兩個 `m != "Kuruwa"` 的訊息，然後要在第三次為 `m == "Kuruwa"` 生成對應的 signature。

它的 $k$ 的生成方式是由以下 code 生成的:

```python
k = int(md5(b'secret').hexdigest() + md5(long_to_bytes(prikey.secret_multiplier) + h).hexdigest(), 16)
```

由於 `md5("secret")` 是已知的，而後面的未知的部分只是個 128 bits 的未知數，所以可以表示為 $k_c+k_i$。之後可以針對兩個 signature 列出以下等式:

$$
\begin{aligned}
s_1 (k_c + k_1) &\equiv h_1 + r_1 d \pmod{n} \\\\
s_2 (k_c + k_2) &\equiv h_2 + r_2 d \pmod{n}
\end{aligned}
$$

然後可以用 resultant 把兩式中的 $d$ 消除，得到

$$
a k_1 + b k_2 +c \equiv 0 \pmod{n}
$$

這邊的一個作法是把整式除 $a$，然後使用[此處的 5.2.1 Lattice Attack](https://eprint.iacr.org/2020/1506.pdf) 的做法可以在一個 Lattice 的短向量中找到 $k_1, k_2$。不過我這邊採用的是一個不一樣的做法。

[rkm0959/Inequality_Solving_with_CVP](https://github.com/rkm0959/Inequality_Solving_with_CVP) 這個 repo 提供了一個使用 Babai CVP 的腳本 (`solver.sage`)，可以提供一些不等式(以矩陣 $B$ 表達)以及它的上下界($\mathit{lb}$ 和 $\mathit{ub}$)，之後它會對矩陣和上下界做一些 scaling 之後用 Babai CVP 去逼近 $\frac{\mathit{lb}+\mathit{ub}}{2}$ 嘗試找到解答。

這題的話可以用以下的 basis:

$$
B =
\begin{bmatrix}
n & 0 & 0 \\\\
a & 1 & 0 \\\\
b & 0 & 1
\end{bmatrix}
$$

我們知道存在一個 $\vec{x}$ 使得 $\vec{x}B=(-c,k_1,k_2)$，所以可以取

$$
\begin{aligned}
\mathit{lb}&=(-c,0,0) \\\\
\mathit{ub}&=(-c,2^{128},2^{128})
\end{aligned}
$$

作為不等式的上下界，之後丟進 solver 所找出來的向量有高機率就是 $\vec{x}B=(-c,k_1,k_2)$，然後從這邊可以推回 $d$，之後 sign `"Kuruwa"` 傳過去就有 flag 了。

* `solve.sage`: 解題腳本
* `solver.sage`: 從[此處](https://github.com/rkm0959/Inequality_Solving_with_CVP/blob/main/solver.sage)下載下來的腳本

因為 signature 收集的數量不夠多，有些時候找到的 $k_1, k_2$ 不一定是對的，失敗的時候就重新跑一次腳本即可。
