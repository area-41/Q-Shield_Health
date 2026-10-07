"""Módulo de I/O em streaming para manipulação de contêineres .qgh."""

from qshield.io.stream import decrypt_genomic_stream, encrypt_genomic_stream

__all__ = [
    "encrypt_genomic_stream",
    "decrypt_genomic_stream",
]