# Q-Shield Health: Post-Quantum Genomic Data Security Framework

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20(ML--KEM)-orange)
![License](https://img.shields.io/badge/license-MIT-green)

[Português](README.md) | [English](README.en.md) | [Español](README.es.md) | [中文](README.zh.md)

## Overview

Q-Shield Health is an enterprise security framework designed to protect high-throughput genomic data (FASTQ, BAM, VCF) against quantum computing threats. Built around **Hybrid Envelope Encryption**, it pairs the efficiency of **AES-256-GCM** with the post-quantum key encapsulation standard **ML-KEM** (NIST FIPS 203).

## Quickstart (via `uv`)

```bash
git clone [https://github.com/Area-41/q-shield-health.git](https://github.com/Area-41/q-shield-health.git)
cd q-shield-health
uv venv && source .venv/bin/activate
uv pip install -e .