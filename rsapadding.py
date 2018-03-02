import rsa_local as rsa

(puba, priva) = rsa.newkeys(128)
(pubb, privb) = rsa.newkeys(128, (priva.p, priva.q))
(pubc, privc) = rsa.newkeys(128, (priva.p, priva.q))

msg = 52

def encrypt(msg, key):
    return pow(msg, key.e, key.n)

def decrypt(msg, key):
    return pow(msg, key.d, key.n)


ea = encrypt(msg, puba)
eba = encrypt(ea, pubb)
ecba = encrypt(eba, pubc)

da = decrypt(ecba, privb)
dc = decrypt(da, privc)
print(decrypt(dc,priva))
