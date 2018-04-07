# RSA Key Generator
# http://inventwithpython.com/hacking (BSD Licensed)

import crypto.cryptomath as cryptomath
import crypto.rabinMiller as rabinMiller
import random


class SRA_key():
    def __init__(self, keysize, pq):
        self.keysize = keysize
        self.generateKey(self.keysize, pq)

    @classmethod
    def from_new_primes(cls, keysize):
        pq = cls.generate_primes(keysize)
        return cls(keysize, pq)

    @classmethod
    def from_existing_primes(cls, keysize, pq):
        return cls(keysize, pq)

    def generate_primes(keysize):
        # Step 1: Create two prime numbers, p and q. Calculate n = p * q.
        print('Generating p prime...')
        p = rabinMiller.generateLargePrime(keysize)
        print('Generating q prime...')
        q = rabinMiller.generateLargePrime(keysize)
        return (p, q)

    def generateKey(self, keySize, pq=None):
        # Creates a public/private key pair with keys that are keySize bits in
        # size. This function may take a while to run.
        if(pq is None):
            # Step 1: Create two prime numbers, p and q. Calculate n = p * q.
            print('Generating p prime...')
            p = rabinMiller.generateLargePrime(keySize)
            print('Generating q prime...')
            q = rabinMiller.generateLargePrime(keySize)
        else:
            print("Using pre-generated primes")
            p, q = pq
        n = p * q

        # Step 2: Create a number e that is relatively prime to (p-1)*(q-1).
        print('Generating e that is relatively prime to (p-1)*(q-1)...')
        while True:
            # Keep trying random numbers for e until one is valid.
            e = random.randrange(2 ** (keySize - 1), 2 ** (keySize))
            if cryptomath.gcd(e, (p - 1) * (q - 1)) == 1:
                break

        # Step 3: Calculate d, the mod inverse of e.
        print('Calculating d that is mod inverse of e...')
        d = cryptomath.findModInverse(e, (p - 1) * (q - 1))

        self.n = n
        self.e = e
        self.d = d
        self.pq = (p, q)

    def encrypt_message(self, message):
        return(pow(message, self.e, self.n))

    def decrypt_message(self, message):
        return(pow(message, self.d, self.n))

    def get_public_primes(self):
        return self.pq

    def get_private_component(self):
        return self.d

    def update_private_component(self, d):
        self.d = d
