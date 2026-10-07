"""Interface de Linha de Comando (CLI) para o Q-Shield Health."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from qshield.crypto.engine import KeyGenError, generate_pqc_keypair
from qshield.io.stream import decrypt_genomic_stream, encrypt_genomic_stream

app = typer.Typer(
    name="qshield",
    help="Q-Shield Health: Post-Quantum Genomic Data Security Framework",
    add_completion=False,
)
console = Console()


@app.command("keygen")
def keygen(
    out_dir: Annotated[
        Path,
        typer.Option("--out", "-o", help="Diretório de saída das chaves"),
    ] = Path("."),
    algorithm: Annotated[
        str,
        typer.Option("--alg", "-a", help="Algoritmo PQC (ML-KEM-768 / ML-KEM-1024)"),
    ] = "ML-KEM-768",
) -> None:
    """Gera um par de chaves assimétricas pós-quânticas ML-KEM."""
    try:
        console.print(f"[bold blue]Gerando par de chaves PQC ({algorithm})...[/bold blue]")
        kp = generate_pqc_keypair(algorithm)

        out_dir.mkdir(parents=True, exist_ok=True)
        pk_path = out_dir / "genomic_pqc.pub"
        sk_path = out_dir / "genomic_pqc.key"

        pk_path.write_bytes(kp.public_key)
        sk_path.write_bytes(kp.secret_key)

        console.print(f"[bold green]Chave Pública salva em:[/bold green] {pk_path}")
        console.print(f"[bold green]Chave Privada salva em:[/bold green] {sk_path}")
    except (KeyGenError, OSError) as e:
        console.print(f"[bold red]Erro ao gerar chaves:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("encrypt")
def encrypt(
    input_file: Annotated[
        Path,
        typer.Option("--input", "-i", help="Arquivo genômico de entrada (FASTQ/BAM/VCF)"),
    ],
    output_file: Annotated[
        Path,
        typer.Option("--output", "-o", help="Caminho do container .qgh cifrado"),
    ],
    pubkey_path: Annotated[
        Path,
        typer.Option("--pubkey", "-p", help="Caminho da chave pública PQC (.pub)"),
    ],
    algorithm: Annotated[
        str,
        typer.Option("--alg", "-a", help="Variante PQC"),
    ] = "ML-KEM-768",
) -> None:
    """Cifra um arquivo genômico em streaming e gera o container .qgh."""
    try:
        pubkey = pubkey_path.read_bytes()
        with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
            encrypt_genomic_stream(f_in, f_out, pubkey, algorithm)
        console.print(f"[bold green]Arquivo cifrado com sucesso:[/bold green] {output_file}")
    except (KeyGenError, OSError, ValueError) as e:
        console.print(f"[bold red]Erro na cifragem:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("decrypt")
def decrypt(
    input_file: Annotated[
        Path,
        typer.Option("--input", "-i", help="Container .qgh cifrado"),
    ],
    output_file: Annotated[
        Path,
        typer.Option("--output", "-o", help="Caminho do arquivo genômico restaurado"),
    ],
    seckey_path: Annotated[
        Path,
        typer.Option("--seckey", "-k", help="Caminho da chave privada PQC (.key)"),
    ],
) -> None:
    """Desembala o container e restaura o arquivo genômico original."""
    try:
        seckey = seckey_path.read_bytes()
        with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
            decrypt_genomic_stream(f_in, f_out, seckey)
        console.print(f"[bold green]Arquivo restaurado com sucesso:[/bold green] {output_file}")
    except (KeyGenError, OSError, ValueError) as e:
        console.print(f"[bold red]Erro na decifragem:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()