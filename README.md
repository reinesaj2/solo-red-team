⚠️ Educational Use Only: All examples are fictional and for learning purposes. Do not use against systems without explicit written authorization.

# Cybersecurity Portfolio Project: Web Application & Authentication Security Analysis

> Recruiter note: Demonstrates red‑team simulation in a controlled lab; no live targets.

## Project Overview

This repository showcases a comprehensive analysis of web application and system-level authentication vulnerabilities. The project demonstrates core competencies in vulnerability assessment, ethical hacking, and defensive engineering, conducted in a secure, isolated lab environment. All attack simulations were performed against intentionally vulnerable targets to develop and test defensive strategies.

## How to run safely

- Run locally with the sandboxed lab (Docker). Prefer offline/isolated network.
- Start lab services:
```bash
docker compose -f lab/docker-compose.yml up -d
```
- Stop and clean up:
```bash
docker compose -f lab/docker-compose.yml down -v
```
- Never target real hosts. See `lab/README.md` for isolation guidance.

## Architecture

Mermaid source: `docs/architecture.mmd`. Render to PNG (example):
```bash
mmdc -i docs/architecture.mmd -o docs/architecture.png
```

## Core Competencies & Key Accomplishments

*   **Vulnerability Assessment:** Identified critical security weaknesses in legacy and modern authentication mechanisms, including Basic, Digest, NTLM, and salted SHA-512.
*   **Offline Password Cracking:** Successfully executed dictionary and rule-based attacks using John the Ripper and Ophcrack to recover passwords from Windows and Linux hash dumps, demonstrating a deep understanding of password hashing vulnerabilities.
*   **Online Brute-Force Attacks:** Conducted distributed brute-force attacks against web authentication forms (HTML, Basic, Digest) using Hydra, achieving a high success rate while managing attack signatures.
*   **Advanced Attack Execution:**
    *   **Parameter Pollution:** Exploited a parameter pollution vulnerability to bypass security controls.
    *   **Credential Reuse:** Simulated privilege escalation by identifying and leveraging reused credentials across multiple services.
    *   **Nonce Reuse Attack:** Defeated Digest authentication by exploiting a nonce reuse flaw.
    *   **Timing Attacks:** Developed and implemented timing attacks to extract sensitive information from authentication endpoints.
*   **Systematic Reporting:** Produced comprehensive documentation, including detailed command logs, evidence artifacts, and a final security assessment report, demonstrating strong communication and analytical skills.

## Module summary

| Module | Purpose | Key scripts | Outputs |
|---|---|---|---|
| Recon | Fingerprint services and auth schemes | `response_fingerprint.py` | service map, headers |
| Exploitation | Online/offline auth testing | `credential_reuse.py`, `digest_nonce_reuse.py`, `timing_attack.py` | attempt logs, findings |
| Reporting | Aggregate and explain findings | `report/` LaTeX and PNGs | final report, visuals |

## Detection Engineering Insight

- Failed‑auth telemetry, nonce issuance cadence, and response size variance can signal brute‑force and digest replay. Rate‑limit challenges, bind nonce to client tuple, and randomize static response sizes.
- Password reuse signals across services inform hardening and user training; enforce unique credentials and breached‑password checks.

## Evidence & Reporting

**Sanitization Note:** All evidence and logs in this repository have been sanitized. This project demonstrates security assessment capabilities in a controlled, ethical context.

The `evidence/` directory contains sanitized artifacts only (raw evidence excluded by `.gitignore`). Includes:

*   **Attack Summaries:** Detailed summaries of the basic and advanced attack phases.
*   **Log Files:** Sanitized output from tools like Hydra and Patator.
*   **Screenshots:** Redacted CLI output, no real credentials.
*   **Command Logs:** A log of the commands that were executed.

## Methodology

This project followed a structured, five-phase ethical hacking methodology:

1.  **Reconnaissance:** Fingerprinted target systems and applications to map the attack surface and identify authentication mechanisms.
2.  **Initial Access:** Gained an initial foothold by exploiting weak passwords and common vulnerabilities in a controlled lab setting.
3.  **Privilege Escalation & Lateral Movement:** Escalated privileges by leveraging credential reuse and other vulnerabilities.
4.  **Advanced Exploitation:** Deployed sophisticated techniques, including nonce reuse and timing attacks, against hardened targets.
5.  **Reporting:** Meticulously documented all findings, attack paths, and recommendations in a professional security assessment report.

---

Ethical statement: The author supports responsible disclosure and safe training. All examples are fictional and for learning purposes only.
