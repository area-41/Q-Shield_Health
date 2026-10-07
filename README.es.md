# Q-Shield Health: Marco de Seguridad para Datos Genómicos Post-Cuánticos

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20(ML--KEM)-orange)
![License](https://img.shields.io/badge/license-MIT-green)

[Português](README.md) | [English](README.en.md) | [Español](README.es.md) | [中文](README.zh.md)

## Resumen

Q-Shield Health es una solución criptográfica empresarial diseñada para proteger archivos genómicos de alto rendimiento (FASTQ, BAM, VCF) contra amenazas de computación cuántica mediante el uso de **Cifrado en Sobre Híbrido** (ML-KEM + AES-256-GCM).

## Uso Rápido

```bash
git clone [https://github.com/Area-41/q-shield-health.git](https://github.com/Area-41/q-shield-health.git)
cd q-shield-health
uv venv && source .venv/bin/activate
uv pip install -e .