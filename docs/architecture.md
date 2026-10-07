# Q-Shield Health: Technical Architecture Specification

## Overview

Q-Shield Health implements a **Hybrid Envelope Encryption Architecture** optimized for high-throughput genomic data files (FASTQ, BAM, VCF). 

By decoupling data encryption from key encapsulation, the architecture delivers constant quantum-resistant overhead regardless of file size (from MBs to TBs).

## Core Components

1. **Ingestion Layer**: Reads large binary/text streams from genomic sequencers using a chunked buffer strategy (`CHUNK_SIZE = 64MB`).
2. **Key Encapsulation Mechanism (KEM)**: Uses **ML-KEM-768 / ML-KEM-1024** (NIST FIPS 203) to encapsulate a 256-bit ephemeral Data Encryption Key (DEK).
3. **Symmetric Data Cipher**: Uses **AES-256-GCM** (Galois/Counter Mode) providing authenticated encryption (AEAD) over genomic chunks.
4. **Binary Container (.qgh)**: Custom binary layout containing protocol metadata, encrypted KEK ciphertext, initialization vector (nonce), and authenticated payload chunks.

## Binary Container Layout (.qgh)

```text
+-------------------+-----------------+-------------------+
| Magic Bytes (4B)  | Version (1B)    | Alg ID (1B)       |
+-------------------+-----------------+-------------------+
| KEK Length (2B)   | KEK Ciphertext (Var: 1088B/1568B)   |
+-------------------+-----------------+-------------------+
| GCM Nonce (12B)   | Encrypted Payload Streams...      |
+-------------------+-------------------------------------+

```mermaid
sequenceDiagram
    autonumber
    participant App as CLI / Pipeline Engine
    participant CSPRNG as Crypto Secure RNG
    participant KEM as ML-KEM Module (FIPS 203)
    participant AES as AES-256-GCM Engine
    participant Storage as Binary File (.qgh)

    App->>CSPRNG: Solicita chave simétrica efêmera (DEK - 256 bits)
    CSPRNG-->>App: Retorna DEK
    App->>KEM: crypto_kem_encaps(pk_recipient, DEK)
    Note over KEM: Encapsula a DEK utilizando a Chave Pública PQC
    KEM-->>App: Retorna Ciphertext da Chave (KEK Ciphertext)
    App->>CSPRNG: Solicita Nonce GCM efêmero (96 bits)
    CSPRNG-->>App: Retorna Nonce
    App->>Storage: Escreve Cabeçalho Binary (Magic, Version, AlgID, KEK Ciphertext, Nonce)
    
    loop Stream em Chunks de Dados Genômicos (FASTQ/BAM)
        App->>AES: Stream Chunk + DEK + Nonce
        AES-->>App: Retorna Ciphertext Chunk
        App->>Storage: Escreve Encrypted Chunk
    end
    
    App->>AES: Finaliza Stream
    AES-->>App: Retorna Authentication Tag (128 bits)
    App->>Storage: Escreve GCM Auth Tag
```

```mermaid
sequenceDiagram
    autonumber
    participant App as CLI / Pipeline Engine
    participant Storage as Binary File (.qgh)
    participant KEM as ML-KEM Module (FIPS 203)
    participant AES as AES-256-GCM Engine
    participant Output as Genomic Plaintext Stream

    App->>Storage: Lê Header (Magic, Version, AlgID, KEK Ciphertext, Nonce)
    App->>KEM: crypto_kem_decap(sk_recipient, KEK_Ciphertext)
    Note over KEM: Decapsula e recupera a DEK
    
    alt Falcon / Kyber Auth Failure
        KEM-->>App: Erro de Decapsulamento / Rejeição Implícita
        App->>App: Aborta Execução (Invalid Key)
    else Sucesso
        KEM-->>App: Retorna DEK (256 bits)
    end

    loop Stream em Chunks de Dados Cifrados
        App->>Storage: Lê Encrypted Chunk
        App->>AES: Decrypt Chunk (Chunk, DEK, Nonce)
        AES-->>App: Retorna Plaintext Chunk
        App->>Output: Escreve Plaintext Chunk
    end

    App->>AES: Valida GCM Tag
    alt Tag Mismatch (Tampering)
        AES-->>App: Authentication Error
        App->>Output: Apaga stream parcial e Lança Exceção
    else Valid Tag
        AES-->>App: Integridade Confirmada
    end
```