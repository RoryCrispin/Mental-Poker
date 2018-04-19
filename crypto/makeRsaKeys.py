# coding=utf-8
# RSA Key Generator
# http://inventwithpython.com/hacking (BSD Licensed)

import random
from asyncio import sleep

import crypto.cryptomath as cryptomath
import crypto.rabinMiller as rabinMiller


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
        print('Generating p prime...')
        p = rabinMiller.generateLargePrime(keysize)
        print('Generating q prime...')
        q = rabinMiller.generateLargePrime(keysize)
        return p, q

    def generateKey(self, key_size, pq=None):
        # Creates a public/private key pair with keys that are keySize bits in
        # size. This function may take a while to run.
        if pq is None:
            # Step 1: Create two prime numbers, p and q. Calculate n = p * q.
            print('Generating p prime...')
            p = rabinMiller.generateLargePrime(key_size)
            print('Generating q prime...')
            q = rabinMiller.generateLargePrime(key_size)
        else:
            print("Using pre-generated primes")
            p, q = pq
        n = p * q

        # Step 2: Create a number e that is relatively prime to (p-1)*(q-1).
        print('Generating e that is relatively prime to (p-1)*(q-1)...')
        while True:
            # Keep trying random numbers for e until one is valid.
            e = random.randrange(2 ** (key_size - 1), 2 ** key_size)
            if cryptomath.gcd(e, (p - 1) * (q - 1)) == 1:
                break

        # Step 3: Calculate d, the mod inverse of e.
        print('Calculating d that is mod inverse of e...')
        d = cryptomath.find_mod_inverse(e, (p - 1) * (q - 1))

        self.n = n
        self.e = e
        self.d = d
        self.pq = (p, q)

        print("Using e = {}".format(e))

    def bruteforce_key(self, key_size, pq, ciphertext, expected):
        self.p, self.q = pq
        self.n = self.p * self.q

        for e in range(2 ** (key_size - 1), 2 ** key_size):
            if cryptomath.gcd(e, (self.p - 1) * (self.q - 1)) == 1:
                self.d = cryptomath.find_mod_inverse(e, (self.p - 1) * (self.q - 1))
                self.e = e
                print("Checking e = {}".format(e))
                sleep(1)
                if self.decrypt_message(ciphertext) == expected:
                    print("DONE")
                    return e

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
