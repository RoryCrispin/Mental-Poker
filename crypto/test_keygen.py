# coding=utf-8
from crypto.sra_keygen import SraKey


def test_enc_dec_works():
    ka = SraKey.from_new_primes(1024)
    ea = ka.encrypt_message(52)
    da = ka.decrypt_message(ea)
    assert da == 52


def test_ea_eb_not_equal():
    ka = SraKey.from_new_primes(1024)
    kb = SraKey.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eb = kb.encrypt_message(message)
    assert ea != eb


def test_commutativity():
    ka = SraKey.from_new_primes(1024)
    kb = SraKey.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eba = kb.encrypt_message(ea)

    assert ea != eba

    da_eba = ka.decrypt_message(eba)
    dab_eba = kb.decrypt_message(da_eba)

    assert dab_eba == message


def test_commutativity_three_way():
    ka = SraKey.from_new_primes(1024)
    kb = SraKey.from_existing_primes(1024, ka.get_public_primes())
    kc = SraKey.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eba = kb.encrypt_message(ea)
    ecba = kc.encrypt_message(eba)

    assert ea != eba
    assert eba != ecba

    da_ecba = ka.decrypt_message(ecba)
    dab_ecba = kb.decrypt_message(da_ecba)
    dcab_ecba = kc.decrypt_message(dab_ecba)

    assert dcab_ecba == message


def test_share_provate_d_commutativity():
    ka = SraKey.from_new_primes(1024)
    kb = SraKey.from_existing_primes(1024, ka.get_public_primes())
    kc = SraKey.from_existing_primes(1024, ka.get_public_primes())

    message = 52
    ea = ka.encrypt_message(message)
    eba = kb.encrypt_message(ea)
    ecba = kc.encrypt_message(eba)

    assert ea != eba
    assert eba != ecba

    bd = kb.get_private_component()
    cd = kc.get_private_component()

    da_ecba = ka.decrypt_message(ecba)

    ka.update_private_component(bd)
    dab_ecba = ka.decrypt_message(da_ecba)

    ka.update_private_component(cd)
    dcab_ecba = ka.decrypt_message(dab_ecba)

    assert dcab_ecba == message
