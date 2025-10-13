⚠️ Legal & Ethical Notice: Do not use any code in this repo against systems without explicit written authorization. The author will not assist or condone misuse.

# Cybersecurity Portfolio Project: Web Application & Authentication Security Analysis

## Project Overview

This repository showcases a comprehensive analysis of web application and system-level authentication vulnerabilities. The project demonstrates core competencies in vulnerability assessment, ethical hacking, and defensive engineering, conducted in a secure, isolated lab environment. All attack simulations were performed against intentionally vulnerable targets to develop and test defensive strategies.

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

## How to run safely
Safe lab instructions: docker-compose -f lab/docker-compose.yml up creates the vulnerable environment. Do not run tools against any networked system you do not own. See lab/README.md for required isolation steps.

## Tools & Technologies

*   **Password Analysis:** John the Ripper, Ophcrack, Hydra, Patator, Crunch
*   **Web Application Testing:** Curl, Custom Python & Bash Scripts
*   **Operating Systems:** Windows 7, Windows 2003, Linux (Ubuntu)
*   **Scripting & Automation:** Python, Bash

## Methodology

This project followed a structured, five-phase ethical hacking methodology:

1.  **Reconnaissance:** Fingerprinted target systems and applications to map the attack surface and identify authentication mechanisms.
2.  **Initial Access:** Gained an initial foothold by exploiting weak passwords and common vulnerabilities in a controlled lab setting.
3.  **Privilege Escalation & Lateral Movement:** Escalated privileges by leveraging credential reuse and other vulnerabilities.
4.  **Advanced Exploitation:** Deployed sophisticated techniques, including nonce reuse and timing attacks, against hardened targets.
5.  **Reporting:** Meticulously documented all findings, attack paths, and recommendations in a professional security assessment report.

## Evidence & Reporting

**Sanitization Note:** All evidence and logs in this repository have been sanitized. This project demonstrates security assessment capabilities in a controlled, ethical context.

The `evidence/` directory contains a comprehensive collection of artifacts from this engagement, including:

*   **Attack Summaries:** Detailed summaries of the basic and advanced attack phases.
*   **Log Files:** Raw output from tools like Hydra and Patator.
*   **Password Lists:** The passwords that were successfully cracked.
*   **Command Logs:** A log of the commands that were executed.

This project demonstrates the ability to think like an attacker to identify and exploit complex vulnerabilities, providing the foundation for building stronger, more resilient defensive systems.
