"""Testes unitários para a engine criptográfica ML-KEM e AES-256-GCM."""

import pytest

from qshield.crypto.engine import (
    KeyGenError,
    decapsulate_dek,
    encapsulate_dek,
    generate_pqc_keypair,
)


def test_generate_pqc_keypair_success() -> None:
    """Verifica a geração correta do par de chaves ML-KEM-768."""
    kp = generate_pqc_keypair("ML-KEM-768")
    assert kp.public_key is not None
    assert kp.secret_key is not None
    assert len(kp.public_key) > 0
    assert len(kp.secret_key) > 0
    assert kp.algorithm == "ML-KEM-768"


def test_generate_pqc_keypair_1024() -> None:
    """Verifica a geração do par de chaves ML-KEM-1024."""
    kp = generate_pqc_keypair("ML-KEM-1024")
    assert kp.algorithm == "ML-KEM-1024"


def test_generate_pqc_keypair_invalid_algorithm() -> None:
    """Garante que exceção é lançada para algoritmo não suportado."""
    with pytest.raises(KeyGenError):
        generate_pqc_keypair("INVALID-KEM")


def test_encapsulate_decapsulate_cycle() -> None:
    """Testa o ciclo completo de encapsulamento e decapsulamento da DEK."""
    kp = generate_pqc_keypair("ML-KEM-768")
    ciphertext, shared_secret_enc = encapsulate_dek(kp.public_key, "ML-KEM-768")
    shared_secret_dec = decapsulate_dek(ciphertext, kp.secret_key, "ML-KEM-768")

    assert shared_secret_enc == shared_secret_dec
    assert len(shared_secret_enc) == 32  # 256-bit symmetric key
