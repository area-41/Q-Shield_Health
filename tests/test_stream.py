"""Testes de integração para criptografia/desencriptação em streaming (.qgh)."""

import io

import pytest

from qshield.crypto.engine import generate_pqc_keypair
from qshield.io.stream import decrypt_genomic_stream, encrypt_genomic_stream


def test_genomic_stream_roundtrip() -> None:
    """Testa a integridade completa de ponta a ponta na cifragem/decifragem de um stream."""
    # Gera dados genômicos sintéticos simulando um arquivo FASTQ
    sample_data = (
        b"@SEQ_ID_001\nGATCGATCGATCGATCGATCGATCGATC\n+\nIIIIIIIIIIIIIIIIIIIIIIIIIIII\n"
        * 100
    )

    input_stream = io.BytesIO(sample_data)
    encrypted_stream = io.BytesIO()
    restored_stream = io.BytesIO()

    kp = generate_pqc_keypair("ML-KEM-768")

    # Cifra o stream de dados
    encrypt_genomic_stream(input_stream, encrypted_stream, kp.public_key, "ML-KEM-768")
    encrypted_stream.seek(0)

    # Decifra o stream de dados
    decrypt_genomic_stream(encrypted_stream, restored_stream, kp.secret_key)
    restored_stream.seek(0)

    # Valida integridade exata byte a byte
    assert restored_stream.read() == sample_data


def test_decrypt_invalid_magic_bytes() -> None:
    """Garante falha ao tentar decifrar arquivo com cabeçalho corrompido."""
    corrupted_stream = io.BytesIO(b"INVALID_HEADER_DATA_1234567890")
    output_stream = io.BytesIO()
    kp = generate_pqc_keypair("ML-KEM-768")

    with pytest.raises(ValueError, match="Magic Bytes incompatíveis"):
        decrypt_genomic_stream(corrupted_stream, output_stream, kp.secret_key)
