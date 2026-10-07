# Q-Shield Health: 后量子基因组数据安全框架

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20(ML--KEM)-orange)
![License](https://img.shields.io/badge/license-MIT-green)

[Português](README.md) | [English](README.en.md) | [Español](README.es.md) | [中文](README.zh.md)

## 概述

Q-Shield Health 是一个企业级安全框架，旨在利用**混合信封加密** (ML-KEM 与 AES-256-GCM) 保护高通量基因组数据（FASTQ、BAM、VCF）免受量子计算威胁。

## 快速开始

```bash
git clone [https://github.com/Area-41/q-shield-health.git](https://github.com/Area-41/q-shield-health.git)
cd q-shield-health
uv venv && source .venv/bin/activate
uv pip install -e .