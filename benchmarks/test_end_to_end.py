"""Script de Teste de Integração End-to-End (E2E) para o Q-Shield Health."""

import hashlib
from pathlib import Path
import tempfile
from qshield.crypto.engine import generate_pqc_keypair
from qshield.io.stream import decrypt_genomic_stream, encrypt_genomic_stream


def calculate_sha256(file_path: Path) -> str:
    """Calcula o hash SHA-256 de um arquivo em disco."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_e2e_test() -> None:
    """Executa o teste de ponta a ponta: geração de chaves, cifragem, decifragem e checagem de hash."""
    print("=== Iniciando Teste de Integração End-to-End (PQC ML-KEM) ===")

    sample_fastq_content = (
        b"@SEQ_ID_001\n"
        b"GATCGATCGATCGATCGATCGATCGATCGATCGATC\n"
        b"+\n"
        b"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII\n"
        b"@SEQ_ID_002\n"
        b"ATCGATCGATCGATCGATCGATCGATCGATCGATCG\n"
        b"+\n"
        b"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII\n"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        original_file = tmp_path / "test_genome.fastq"
        encrypted_file = tmp_path / "test_genome.fastq.qgh"
        restored_file = tmp_path / "restored_genome.fastq"

        # 1. Escrever o arquivo FASTQ sintético
        original_file.write_bytes(sample_fastq_content)
        original_hash = calculate_sha256(original_file)
        print(f"1. Arquivo FASTQ original criado. SHA-256: {original_hash}")

        # 2. Gerar Par de Chaves PQC (ML-KEM-768)
        print("2. Gerando par de chaves ML-KEM-768...")
        keypair = generate_pqc_keypair("ML-KEM-768")

        # 3. Cifrar (Streaming / Envelope)
        print("3. Cifrando o arquivo genômico em container .qgh...")
        with open(original_file, "rb") as f_in, open(encrypted_file, "wb") as f_out:
            encrypt_genomic_stream(f_in, f_out, keypair.public_key, "ML-KEM-768")

        print(f"   Container cifrado gerado ({encrypted_file.stat().st_size} bytes)")

        # 4. Decifrar (Desembalar)
        print("4. Desembalando o container e restaurando o arquivo...")
        with open(encrypted_file, "rb") as f_in, open(restored_file, "wb") as f_out:
            decrypt_genomic_stream(f_in, f_out, keypair.secret_key)

        restored_hash = calculate_sha256(restored_file)
        print(f"5. Arquivo restaurado. SHA-256: {restored_hash}")

        # 5. Validação de Integridade
        assert original_hash == restored_hash, "FALHA: Os hashes SHA-256 não correspondem!"
        print("\nSUCESSO: Os hashes SHA-256 são exatamente idênticos! Teste concluído com êxito.")


if __name__ == "__main__":
    run_e2e_test()