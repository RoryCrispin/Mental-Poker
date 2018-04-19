from crypto.makeRsaKeys import SraKey

ka = SraKey.from_new_primes(2048)
kb = SraKey.from_existing_primes(2048, ka.get_public_primes())
ea = ka.encrypt_message(52)
kb.bruteforce_key(64, ka.get_public_primes(), ea, 52)

# 15879625741263821173
# 9223372036854775811
