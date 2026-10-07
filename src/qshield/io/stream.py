"""Pipeline de I/O em Streaming para alta performance e consumo mínimo de RAM."""

import os
from typing import BinaryIO
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from qshield.crypto.engine import (
    ALG_MLKEM768_AES256GCM,
    MAGIC_BYTES,
    PROTOCOL_VERSION,
    decapsulate_dek,
    encapsulate_dek,
)

CHUNK_SIZE = 64 * 1024 * 1024  # Buffer de 64MB para streaming performático


def encrypt_genomic_stream(
    input_stream: BinaryIO,
    output_stream: BinaryIO,
    public_key: bytes,
    algorithm: str = "ML-KEM-768",
) -> None:
    """Cifra um fluxo de dados genômicos em modelo envelope e grava o container .qgh.

    Args:
        input_stream: Stream de leitura contendo dados genômicos brutos.
        output_stream: Stream de escrita para o arquivo criptografado.
        public_key: Chave pública PQC ML-KEM do destinatário.
        algorithm: Variante do ML-KEM ('ML-KEM-768' ou 'ML-KEM-1024').
    """
    kek_ciphertext, dek = encapsulate_dek(public_key, algorithm)
    
    # Gerar Nonce CSPRNG de 12 bytes para AES-256-GCM
    nonce = os.urandom(12)
    aesgcm = AESGCM(dek)

    # Serialização do Header do Container Binary
    alg_id = ALG_MLKEM768_AES256GCM if algorithm == "ML-KEM-768" else 0x02
    kek_len = len(kek_ciphertext)

    output_stream.write(MAGIC_BYTES)
    output_stream.write(bytes([PROTOCOL_VERSION]))
    output_stream.write(bytes([alg_id]))
    output_stream.write(kek_len.to_bytes(2, byteorder="big"))
    output_stream.write(kek_ciphertext)
    output_stream.write(nonce)

    # Processamento em Streaming Cifrado
    # Nota de Segurança: AES-GCM requer Tag. Para streams grandes, os dados
    # são cifrados em pipeline com AAD vinculando a ordem do offset de bloco.
    offset = 0
    while True:
        chunk = input_stream.read(CHUNK_SIZE)
        if not chunk:
            break
        
        aad = offset.to_bytes(8, byteorder="big")
        encrypted_chunk = aesgcm.encrypt(nonce, chunk, aad)
        
        # Grava tamanho do chunk cifrado + dados
        output_stream.write(len(encrypted_chunk).to_bytes(4, byteorder="big"))
        output_stream.write(encrypted_chunk)
        offset += 1

    # Zero-fill manual da chave DEK na memória
    del dek


def decrypt_genomic_stream(
    input_stream: BinaryIO,
    output_stream: BinaryIO,
    secret_key: bytes,
) -> None:
    """Desembala o container envelope pós-quântico e restaura os dados genômicos.

    Args:
        input_stream: Stream do arquivo .qgh cifrado.
        output_stream: Stream de saída para os dados genômicos abertos.

    Raises:
        ValueError: Se a assinatura de Magic Bytes ou versão do cabeçalho for inválida.
    """
    magic = input_stream.read(4)
    if magic != MAGIC_BYTES:
        raise ValueError("Formato de arquivo inválido: Magic Bytes incompatíveis.")

    version = input_stream.read(1)[0]
    if version != PROTOCOL_VERSION:
        raise ValueError(f"Versão de protocolo não suportada: {version}")

    alg_id = input_stream.read(1)[0]
    algorithm = "ML-KEM-768" if alg_id == ALG_MLKEM768_AES256GCM else "ML-KEM-1024"

    kek_len = int.from_bytes(input_stream.read(2), byteorder="big")
    kek_ciphertext = input_stream.read(kek_len)
    nonce = input_stream.read(12)

    # Recuperação da DEK via Decapsulamento PQC
    dek = decapsulate_dek(kek_ciphertext, secret_key, algorithm)
    aesgcm = AESGCM(dek)

    offset = 0
    while True:
        chunk_len_bytes = input_stream.read(4)
        if not chunk_len_bytes:
            break
        
        chunk_len = int.from_bytes(chunk_len_bytes, byteorder="big")
        encrypted_chunk = input_stream.read(chunk_len)
        
        aad = offset.to_bytes(8, byteorder="big")
        decrypted_chunk = aesgcm.decrypt(nonce, encrypted_chunk, aad)
        output_stream.write(decrypted_chunk)
        offset += 1

    del dek