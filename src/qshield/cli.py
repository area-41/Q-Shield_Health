"""Interface de Linha de Comando (CLI) profissional usando Typer."""

from pathlib import Path

import typer
from rich.console import Console

from qshield.crypto.engine import generate_pqc_keypair
from qshield.io.stream import decrypt_genomic_stream, encrypt_genomic_stream

app = typer.Typer(
    name="qshield",
    help="Q-Shield Health: Post-Quantum Genomic Protection CLI Engine",
    add_completion=False,
)
console = Console()


@app.command("keygen")
def keygen(
    out_dir: Path = typer.Option(
        Path("."), "--out", "-o", help="Diretório de saída das chaves"
    ),
    algorithm: str = typer.Option(
        "ML-KEM-768", "--alg", "-a", help="Algoritmo PQC (ML-KEM-768 / ML-KEM-1024)"
    ),
) -> None:
    """Gera um par de chaves pós-quânticas ML-KEM."""
    console.print(f"[bold blue]Gerando par de chaves PQC ({algorithm})...[/bold blue]")
    try:
        kp = generate_pqc_keypair(algorithm)
        pk_path = out_dir / "genomic_pqc.pub"
        sk_path = out_dir / "genomic_pqc.key"

        pk_path.write_bytes(kp.public_key)
        sk_path.write_bytes(kp.secret_key)

        console.print(f"[bold green]Chave Pública salva em:[/bold green] {pk_path}")
        console.print(f"[bold green]Chave Privada salva em:[/bold green] {sk_path}")
    except Exception as e:
        console.print(f"[bold red]Erro ao gerar chaves:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("encrypt")
def encrypt(
    input_file: Path = typer.Option(
        ..., "--input", "-i", help="Arquivo genômico de entrada (FASTQ/BAM/VCF)"
    ),
    output_file: Path = typer.Option(
        ..., "--output", "-o", help="Caminho do container .qgh cifrado"
    ),
    pubkey_path: Path = typer.Option(
        ..., "--pubkey", "-p", help="Caminho da chave pública PQC (.pub)"
    ),
    algorithm: str = typer.Option("ML-KEM-768", "--alg", "-a", help="Variante PQC"),
) -> None:
    """Cifra arquivo genômico via Criptografia de Envelope PQC."""
    if not input_file.exists():
        console.print(f"[bold red]Arquivo não encontrado:[/bold red] {input_file}")
        raise typer.Exit(code=1)

    pk_bytes = pubkey_path.read_bytes()

    console.print(
        f"[bold yellow]Iniciando Criptografia de Envelope:[/bold yellow] {input_file}"
    )
    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        encrypt_genomic_stream(f_in, f_out, pk_bytes, algorithm)

    console.print(
        f"[bold green]Arquivo Genômico Protegido com Sucesso:[/bold green] {output_file}"
    )


@app.command("decrypt")
def decrypt(
    input_file: Path = typer.Option(
        ..., "--input", "-i", help="Container .qgh cifrado"
    ),
    output_file: Path = typer.Option(
        ..., "--output", "-o", help="Caminho do arquivo genômico restaurado"
    ),
    seckey_path: Path = typer.Option(
        ..., "--seckey", "-k", help="Caminho da chave privada PQC (.key)"
    ),
) -> None:
    """Desembala o container e restaura o arquivo genômico original."""
    if not input_file.exists():
        console.print(f"[bold red]Container não encontrado:[/bold red] {input_file}")
        raise typer.Exit(code=1)

    sk_bytes = seckey_path.read_bytes()

    console.print(
        f"[bold yellow]Iniciando Decapsulamento e Decifragem:[/bold yellow] {input_file}"
    )
    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        decrypt_genomic_stream(f_in, f_out, sk_bytes)

    console.print(
        f"[bold green]Arquivo Genômico Restaurado com Sucesso:[/bold green] {output_file}"
    )


if __name__ == "__main__":
    app()
