"""Engine criptográfica de alto desempenho combinando ML-KEM (FIPS 203) e AES-256-GCM."""

import hashlib
from typing import Tuple
from kyber_py.kyber import Kyber768, Kyber1024

# Identificadores do Protocolo
MAGIC_BYTES = b"QGH1"
PROTOCOL_VERSION = 0x01
ALG_MLKEM768_AES256GCM = 0x01
ALG_MLKEM1024_AES256GCM = 0x02


class KeyGenError(Exception):
    """Exceção para falhas na geração de chaves PQC."""


class CryptoEngineError(Exception):
    """Exceção genérica para falhas na engine criptográfica."""


class Keypair:
    """Contêiner imutável para par de chaves PQC."""

    def __init__(self, public_key: bytes, secret_key: bytes, algorithm: str) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._algorithm = algorithm

    @property
    def public_key(self) -> bytes:
        return self._public_key

    @property
    def secret_key(self) -> bytes:
        return self._secret_key

    @property
    def algorithm(self) -> str:
        return self._algorithm


def _derive_256bit_dek(shared_secret: bytes) -> bytes:
    """Deriva uma chave simétrica DEK de 256 bits a partir do segredo compartilhado."""
    return hashlib.sha256(shared_secret).digest()


def generate_pqc_keypair(algorithm: str = "ML-KEM-768") -> Keypair:
    """Gera um par de chaves assimétricas pós-quânticas ML-KEM."""
    try:
        if algorithm == "ML-KEM-768":
            pk, sk = Kyber768.keygen()
        elif algorithm == "ML-KEM-1024":
            pk, sk = Kyber1024.keygen()
        else:
            raise KeyGenError(f"Algoritmo não suportado: {algorithm}")
        return Keypair(pk, sk, algorithm)
    except Exception as err:
        raise KeyGenError(f"Falha ao gerar par de chaves ML-KEM: {err}") from err


def encapsulate_dek(public_key: bytes, algorithm: str = "ML-KEM-768") -> Tuple[bytes, bytes]:
    """Encapsula uma Chave de Criptografia de Dados (DEK) usando ML-KEM.

    Returns:
        Tuple contendo (kek_ciphertext, dek_256bits)
    """
    if algorithm == "ML-KEM-768":
        shared_secret, ciphertext = Kyber768.encaps(public_key)
    elif algorithm == "ML-KEM-1024":
        shared_secret, ciphertext = Kyber1024.encaps(public_key)
    else:
        raise KeyGenError(f"Algoritmo não suportado: {algorithm}")

    dek = _derive_256bit_dek(shared_secret)
    return ciphertext, dek


def decapsulate_dek(ciphertext: bytes, secret_key: bytes, algorithm: str = "ML-KEM-768") -> bytes:
    """Decapsula a chave simétrica DEK utilizando a chave secreta PQC."""
    if algorithm == "ML-KEM-768":
        shared_secret = Kyber768.decaps(secret_key, ciphertext)
    elif algorithm == "ML-KEM-1024":
        shared_secret = Kyber1024.decaps(secret_key, ciphertext)
    else:
        raise KeyGenError(f"Algoritmo não suportado: {algorithm}")

    return _derive_256bit_dek(shared_secret)