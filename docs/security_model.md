# Q-Shield Health: Threat Model & Quantum Security Analysis

## Threat Vectors

### 1. Harvest-Now, Decrypt-Later (HNDL)
Adversaries intercept encrypted genomic traffic today and store it until Cryptographically Relevant Quantum Computers (CRQCs) become operational.
- **Mitigation**: ML-KEM (FIPS 203) guarantees lattice-based post-quantum security against Shor's and Grover's algorithms.

### 2. Side-Channel Attacks
Timing and power analysis on lattice key exchange.
- **Mitigation**: `liboqs-python` native C bindings enforce constant-time execution during decapsulation.

### 3. Data Tampering & Replay Attacks
Unauthenticated modification of genomic variants in BAM/VCF payloads.
- **Mitigation**: AES-256-GCM AEAD mode with chunk-indexed Additional Authenticated Data (AAD) ensures integrity validation.