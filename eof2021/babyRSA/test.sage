from Crypto.Util.number import *

pow = power_mod
p = getPrime(512)
q = getPrime(512)
n = p * q
m = n ** 2 + 69420
h = (pow(3, 2022, m) * p ** 2 + pow(5, 2022, m) * q ** 2) % m
a = pow(3, 1011, m)
b = pow(5, 1011, m)
k = 69420

B = matrix(ZZ,[
    [m,    0,0,0],
    [-h,   1,0,0],
    [a^2%m,0,1,0],
    [b^2%m,0,0,1]
])
print(B.solve_left(vector([0,1,p^2,q^2])))

lb=[0,1,0,0]
ub=[0,1,2^1024,2^1024]

load('solver.sage')
result, applied_weights, fin=solve(B,lb,ub)
v=vector([x//y for x,y in zip(result,applied_weights)])
print(v)
ans = vector([0,1,p^2,q^2])
print(ans)
if not v[2].is_square():
    R = B.LLL()
    diff = v - ans
    print('try solve')
    print(R.solve_left(diff))
    # lam0 = B.LLL()[0]
    # lam0 = vector([x//y for x,y in zip(lam0, applied_weights)])
    # print('lam0', lam0)
    # for i in range(-10000,10000):
    #     vv=v+lam0*i
    #     if vv[2].is_square():
    #         print('good', i)
else:
    print('already good')

