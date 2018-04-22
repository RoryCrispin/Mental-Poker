# coding=utf-8
# This class uses the structure of the textbook RSA key generation class
# provided by http://inventwithpython.com/hacking (BSD Licensed) - it has been
# mofidied to use the stronger PyCrypto library functions for prime generation
# and also rearranged to generate SRA keys rather than RSA keys.


import random

from Crypto.PublicKey import pubkey
from Crypto.Util.number import getStrongPrime


class SraKey:
    def __init__(self, keysize, pq):
        self.keysize = keysize
        self.n, self.e, self.d, self.pq = None, None, None, None

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
        p = getStrongPrime(keysize)
        q = getStrongPrime(keysize)
        return p, q

    def generateKey(self, key_size, pq=None):
        if pq is None:
            p = getStrongPrime(key_size)
            q = getStrongPrime(key_size)
        else:
            p, q = pq
        n = p * q

        while True:
            # Keep trying random numbers for e until one is valid.
            e = random.randrange(2 ** (key_size - 1), 2 ** key_size)
            if pubkey.GCD(e, (p - 1) * (q - 1)) == 1:
                break

        d = pubkey.inverse(e, (p - 1) * (q - 1))

        self.n = n
        self.e = e
        self.d = d
        self.pq = (p, q)


    def encrypt_message(self, message):
        return pow(message, self.e, self.n)

    def decrypt_message(self, message):
        return pow(message, self.d, self.n)

    def get_public_primes(self):
        return self.pq

    def get_private_component(self):
        return self.d

    def update_private_component(self, d):
        self.d = d
