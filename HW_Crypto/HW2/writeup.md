# Single

這題的橢圓曲線只給了 $p$，$a, b$ 都是未知的。但是它有給你三個點 $G, A, B$，只要拿任兩個點列出以下的方程式就能解出 $a, b$ 了:

$$
\begin{aligned}
y_1^2 &\equiv x_1^3 + ax_1 + b \pmod{p} \\\\
y_2^2 &\equiv x_2^3 + ax_2 + b \pmod{p}
\end{aligned}
$$

解出 $a, b$ 之後用 Sage 的 `EllipticCurve` 試著產生 `EllipticCurve(GF(p), [a, b])` 會失敗，check 一下會發現 $4a^3+27b^2 \equiv 0 \pmod{p}$，所以是條 Singular curve。

嘗試把 $x^3 + ax + b$ 分解看看會發現它是屬於 $(x-\alpha)^2(x-\beta)$ 的形式，所以這個是 Node。定義

$$
\varphi(P(x, y)) = \frac{y+\sqrt{\alpha-\beta}(x-\alpha)}{y-\sqrt{\alpha-\beta}(x-\alpha)}
$$

之後因為 $\varphi$ 是個從 $(\mathbb{E}(\mathbb{F}_p),+)$ 到 $(\mathbb{F}_p,\times)$ 的 group homomorphism，即 $\varphi(P+Q)=\varphi(P) \cdot \varphi(Q)$，所以 $\varphi(A)=\varphi(d_AG)=\varphi(G)^{d_A}$。

試著分解 $p-1$ 可以發現它是相當 smooth 的，所以直接利用 Pohlig-Hellman 在 $\mathbb{F}_p$ 上解 dlog 後就能獲得 $d_A$。

之後只要計算 $S=d_AB$ 之後就能算出 key 去把 flag 解密了，不過因為 Sage 沒辦法支援在這種 Singular curve 上運算，所以直接用原先題目腳本所提供的改一改計算出來比較簡單。

前面第一部分到算出 $d_A$ 的 code 在 `Single/solve1.sage`，然後最後計算 $S$ 和解密 flag 的部分在 `Single/solve2.py` 之中。
