
from makeRsaKeys import SRA_key


def test_enc_dec_works():
    ka = SRA_key.from_new_pimes(1024)
    ea = ka.encrypt_message(52)
    da = ka.decrypt_message(ea)
    assert da == 52


def test_ea_eb_not_equal():
    ka = SRA_key.from_new_pimes(1024)
    kb = SRA_key.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eb = kb.encrypt_message(message)
    assert ea != eb


def test_commutativity():
    ka = SRA_key.from_new_pimes(1024)
    kb = SRA_key.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eba = kb.encrypt_message(ea)

    assert ea != eba

    da_eba = ka.decrypt_message(eba)
    dab_eba  = kb.decrypt_message(da_eba)

    assert dab_eba == message
