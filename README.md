# Dermatopath Melanoma Agent

> **Domain:** Digital Pathology & Quantitative Histopathology
> **Reference Guidelines & Standards:** `College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Dermatopath Melanoma Agent** is an advanced analytical and computational platform implementing Cutaneous Melanoma Microstaging (Breslow/Clark) & Margin Safety. It provides multi-agent evaluation of pathology metrics with cryptographic audit trails and zero-PHI outbound protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`BreslowMicrostagingAgent`**: Specialized Sub-Agent 1 for dermatopath-melanoma-agent
- **`MitoticRateAuditorAgent`**: Specialized Sub-Agent 2 for dermatopath-melanoma-agent
- **`PeripheralMarginAgent`**: Specialized Sub-Agent 3 for dermatopath-melanoma-agent

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/dermatopath-melanoma-agent.git
cd dermatopath-melanoma-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Target entity or specimen identifier
- `--primary`: Primary measurement value (float)
- `--secondary`: Secondary measurement value (float)
- `--critical`: Flag for critical/emergency escalation
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Task / case identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional (default: 0.0) |
| `is_critical_flag` | Critical escalation flag | Optional (default: false) |
| `status_descriptor` | Status descriptor | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable to a secure random value for production deployments:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((1..32 | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) }))
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t dermatopath-melanoma-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key dermatopath-melanoma-agent
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secure-key docker-compose up -d
```

---

## 📁 Project Structure

```
dermatopath-melanoma-agent/
├── agents/                          # Core agent modules
│   ├── api.py                       # FastAPI REST endpoints
│   ├── base.py                      # Security, PHI guard, audit trail
│   ├── learning.py                  # Bayesian calibration engine
│   ├── llm_factory.py               # LLM provider factory
│   ├── metrics.py                   # Prometheus metrics
│   ├── models.py                    # Pydantic data models
│   ├── streamer.py                  # WebSocket telemetry
│   ├── supervisor.py                # Supervisor orchestrator
│   └── workers.py                   # Specialized worker agents
├── dermatopath_melanoma_agent/      # Alternative package structure
├── tests/                           # Test suite
├── web/                             # Web operations console
├── cli.py                           # Main CLI entry point
├── derm_melanoma.py                 # Legacy CLI (v1)
├── enrichment.py                    # Enrichment feature modules
├── simulator.py                     # High-throughput simulator
├── pyproject.toml                   # Project configuration
├── Dockerfile                       # Container build
└── docker-compose.yml               # Container orchestration
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
