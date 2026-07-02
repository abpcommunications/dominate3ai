<div align="center">

# DOMINATE 3AI (D3AI)

**Privacy-first business intelligence, generated entirely on-device.**

D3AI turns your business context into tiered, board-ready intelligence reports using a local LLM — no cloud inference, no data leaving the machine.

*Built by [ABP Communications LLC](https://abpcommunications.com) · Hartford, CT*

</div>

---

## Overview

DOMINATE 3AI is a Streamlit application that generates structured business intelligence reports across three domains — **Strategy**, **Operations**, and **Management** — at multiple depth tiers. Every inference runs locally through [Ollama](https://ollama.com) (`phi3:mini`), so proprietary company context is never sent to a third-party API.

The core value proposition is **privacy without compromise**: teams that can't or won't route sensitive planning data through OpenAI/Anthropic/Google endpoints can still get on-demand, LLM-generated analysis on hardware they control.

## Key Features

- **Local-only inference** — Powered by Ollama running `phi3:mini` on-device. No cloud LLM dependency, no API keys leaving your environment.
- **Tiered report generation** — Choose **Normal**, **Advanced**, or **Monetized** output per report, across Strategy / Operations / Management domains.
- **Document-grounded analysis** — Upload PDFs or Word docs; extracted text is injected as context so reports reflect your actual material.
- **JWT authentication** — SQLite-backed user store with `bcrypt` password hashing and JWT session tokens.
- **Editable prompts** — Per-category custom prompt editing so you can tune the analytical lens for each domain.
- **Branded PDF export** — ReportLab-generated PDFs with a cover page, table of contents (dot leaders), running header/footer, and navy/gold styling.
- **Email delivery** — Send generated reports directly via SMTP.
- **Company logo resolution** — Company dropdown with automatic logo lookup (logo.dev with a Google favicon fallback).

## The "Monetized" / QML Tier — an honest note

The premium report tier applies a **Quantum ML (QML) scoring layer** on top of the standard generation pipeline. To be transparent about what this currently is:

> The QML layer is presently a **deterministic, hash-based scoring heuristic**. It produces consistent, reproducible priority/confidence scores that differentiate the premium tier — but it is *not yet* a genuine quantum or quantum-inspired optimizer.

The **roadmap** (see below) moves this toward real quantum-inspired optimization using **QUBO formulations** and hybrid classical solvers. We flag this distinction deliberately: accurate representation of the current heuristic — with a credible path to the real thing — is the right way to describe the feature.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI                        │
│   (auth · report config · upload · export · email)   │
└───────────────┬─────────────────────────────────────┘
                │
        ┌───────┴────────┐
        │  auth.py        │  JWT · SQLite · bcrypt
        └───────┬────────┘
                │
   ┌────────────┴─────────────┐
   │  Report Generation Engine │
   │  Normal / Advanced /      │──── document context injection
   │  Monetized (QML scoring)  │
   └────────────┬─────────────┘
                │
        ┌───────┴────────┐
        │   Ollama        │  phi3:mini (local inference)
        └────────────────┘
                │
   ┌────────────┴─────────────┐
   │  ReportLab PDF · SMTP     │  branded export & delivery
   └──────────────────────────┘
```

## Tech Stack

| Layer            | Technology                                             |
|------------------|--------------------------------------------------------|
| UI               | Streamlit, `extra-streamlit-components`                |
| Inference        | Ollama (`phi3:mini`)                                    |
| Auth             | PyJWT, SQLite, bcrypt                                   |
| Documents        | pypdf, python-docx                                      |
| Export           | ReportLab (PDF), plain-text                             |
| Email            | Python `smtplib` (Gmail SMTP, STARTTLS)                |
| Images/branding  | Pillow                                                  |

## Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The `phi3:mini` model pulled locally

```bash
# Install Ollama (see ollama.com for your platform), then:
ollama pull phi3:mini
```

### Installation

```bash
git clone https://github.com/<your-org>/dominate3ai.git
cd dominate3ai

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create `.streamlit/secrets.toml` with your SMTP and JWT settings:

```toml
JWT_SECRET = "your-long-random-secret"

[smtp]
host = "smtp.gmail.com"
port = 587
username = "you@gmail.com"
password = "your-gmail-app-password"   # use a Gmail App Password, not your account password
```

> **Note:** Gmail requires an [App Password](https://support.google.com/accounts/answer/185833) — your normal account password will not authenticate over SMTP. Also avoid inline comments inside TOML tables; a parse failure will silently break *all* secrets loading.

### Run

```bash
# Make sure Ollama is serving:
ollama serve

# Warm the model once to avoid a cold-load delay on first request:
ollama run phi3:mini "warmup"

# Launch the app:
streamlit run app_finalv8.py
```

The app will be available at `http://localhost:8501`.

## Usage

1. **Register / log in** — Accounts are stored locally in SQLite with hashed passwords.
2. **Select a company** — Pick from the dropdown; the logo resolves automatically.
3. **(Optional) Upload a document** — PDF or DOCX; its text becomes report context.
4. **Configure the report** — Choose the domain(s) and tier (Normal / Advanced / Monetized).
5. **Generate** — Inference runs locally; results render as formatted bullet-point sections.
6. **Export / send** — Download a branded PDF or plain-text file, or email it directly.

## Deployment

D3AI runs on a modest cloud VM. The reference deployment uses a **GCP `e2-standard-2`** instance with Ollama and Streamlit managed as `systemd` services.

Performance notes for CPU-only instances:
- CPU inference is **functional but slow** — suitable for validation demos, not performance demos.
- Set `keep_alive="30m"` and do a one-time warm-up on login to avoid cold-load penalties.
- For live walkthroughs, **pre-generate reports** so there's no visible inference latency on screen.

Production hardening on the roadmap: static IP, Caddy + Let's Encrypt for TLS, and optionally a GPU instance for faster inference.

## Roadmap

- [ ] Replace the hash-based QML heuristic with genuine **quantum-inspired optimization** (QUBO formulations + hybrid classical solvers)
- [ ] Production infra: static IP, Caddy + Let's Encrypt, GPU instance option
- [ ] Optional workflow-automation integration (evaluating a code-first orchestration engine embedded in the backend)
- [ ] Expanded document-context handling beyond the current character budget

## Project Structure

```
dominate3ai/
├── app_finalv8.py          # Main Streamlit application
├── auth.py                 # JWT / SQLite / bcrypt authentication
├── requirements.txt
├── .streamlit/
│   └── secrets.toml        # SMTP + JWT config (not committed)
└── README.md
```

## About

D3AI is developed by **ABP Communications LLC**, an integrated communications, consulting, technology, and creative services firm based in Hartford, CT.

## License

_Add your chosen license here (e.g. MIT, Apache-2.0, or proprietary)._

---

<div align="center">
<sub>Privacy-first intelligence · runs entirely on your hardware</sub>
</div>
