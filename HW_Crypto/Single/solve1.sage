p = 9631668579539701602760432524602953084395033948174466686285759025897298205383
gx = 5664314881801362353989790109530444623032842167510027140490832957430741393367
gy = 3735011281298930501441332016708219762942193860515094934964869027614672869355
ax = 3829488417236560785272607696709023677752676859512573328792921651640651429215
ay = 7947434117984861166834877190207950006170738405923358235762824894524937052000
bx = 9587224500151531060103223864145463144550060225196219072827570145340119297428
by = 2527809441042103520997737454058469252175392602635610992457770946515371529908
enc = bytes.fromhex(
    "1536c5b019bd24ddf9fc50de28828f727190ff121b709a6c63c4f823ec31780ad30d219f07a8c419c7afcdce900b6e89b37b18b6daede22e5445eb98f3ca2e40"
)

Z = Zmod(p)
P = PolynomialRing(Z, "a,b")
a, b = P.gens()


def poly(x, y):
    return y ^ 2 - (x ^ 3 + a * x + b)


A = poly(ax, ay)
B = poly(bx, by)
print(A)
print(B)
a = (A - B).univariate_polynomial().roots()[0][0]
b = A.subs(a=a).univariate_polynomial().roots()[0][0]
print(f"{a = }")
print(f"{b = }")
assert poly(gx, gy) == 0
assert 4 * a ^ 3 + 27 * b ^ 2 == 0  # singular curve

P = PolynomialRing(Z, "x")
x = P.gen()
fac = factor(x ^ 3 + a * x + b)
print(fac)  # nodes
alpha = [-f.coefficients()[0] for f, e in fac if e == 2][0]
beta = [-f.coefficients()[0] for f, e in fac if e == 1][0]
assert (x - alpha) ^ 2 * (x - beta) == x ^ 3 + a * x + b


def map_to_fp(x, y):
    s = sqrt(alpha - beta)
    return (y + s * (x - alpha)) / (y - s * (x - alpha))


print(factor(p - 1))  # smooth
G = map_to_fp(gx, gy)
A = map_to_fp(ax, ay)
dA = discrete_log(A, G)
assert G ** dA == A
print(f"{dA = }")
