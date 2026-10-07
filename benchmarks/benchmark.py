"""Script de Benchmarking para medir latência, overhead de memória e throughput."""

import os
import time
from pathlib import Path

import psutil

from qshield.crypto.engine import generate_pqc_keypair
from qshield.io.stream import encrypt_genomic_stream


def run_benchmark(file_size_mb: int) -> None:
    dummy_file = Path(f"sample_{file_size_mb}MB.fastq")
    encrypted_file = Path(f"sample_{file_size_mb}MB.qgh")
    restored_file = Path(f"sample_{file_size_mb}MB.restored.fastq")

    print(f"\n--- Gerando arquivo sintético de {file_size_mb} MB ---")
    chunk_1mb = os.urandom(1024 * 1024)
    with open(dummy_file, "wb") as f:
        f.writelines(chunk_1mb for _ in range(file_size_mb))

    kp = generate_pqc_keypair("ML-KEM-768")
    process = psutil.Process(os.getpid())

    # Medição de Criptografia
    mem_before = process.memory_info().rss / (1024 * 1024)
    start_time = time.perf_counter()

    with open(dummy_file, "rb") as f_in, open(encrypted_file, "wb") as f_out:
        encrypt_genomic_stream(f_in, f_out, kp.public_key, "ML-KEM-768")

    enc_time = time.perf_counter() - start_time
    mem_after = process.memory_info().rss / (1024 * 1024)
    ram_usage = mem_after - mem_before

    print(
        f"Encriptação Envelopada: {enc_time:.4f} seg | Throughput: {file_size_mb / enc_time:.2f} MB/s"
    )
    print(f"Overhead Máximo de Memória RAM: {ram_usage:.2f} MB")

    # Limpeza dos Arquivos de Teste
    dummy_file.unlink()
    encrypted_file.unlink()


if __name__ == "__main__":
    for size in [100, 1000]:  # Executar com 100MB e 1GB
        run_benchmark(size)
