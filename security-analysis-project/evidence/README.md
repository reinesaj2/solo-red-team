# Strategic Password Testing Framework

A comprehensive password testing system designed for security research and defensive analysis within controlled lab environments.

## Overview

This framework implements a two-phase strategic approach to password authentication testing, designed to demonstrate security research methodologies while maintaining ethical boundaries and system stability.

### Key Features

- **Context-Aware Password Generation**: Strategically ranked candidates based on common patterns and organizational context
- **Phase-Based Attack Strategy**: Password spraying followed by targeted attacks
- **Advanced Rate Limiting**: ≤2 requests/sec/target with exponential backoff
- **Comprehensive Analytics**: Real-time logging, response fingerprinting, and visualization
- **Ethical Guidelines**: Designed for security research within approved lab scope

## Architecture

### Core Components

1. **`generate_candidates.py`**: Intelligent password candidate generator
2. **`candidates.txt`**: Ranked password candidates (≤10k lines)
3. **`usernames.txt`**: Approved username list for testing scope

### Directory Structure

```
./
├── evidence/               # Evidence and results storage
├── logs/                   # Detailed activity logs
├── generate_candidates.py  # Password candidate generator
├── candidates.txt          # Strategic password list
├── usernames.txt          # Target usernames
└── README.md              # This documentation
```

## Methodology

### Phase A: Password Spray Attack
- **Scope**: Top 30 password candidates across all users and targets
- **Strategy**: Broad coverage to identify weak common passwords
- **Rate Limiting**: Conservative approach to prevent lockouts
- **Success Criteria**: Any successful authentication triggers enhanced logging

### Phase B: Targeted Attack  
- **Scope**: Up to 200 candidates per remaining user
- **Strategy**: User-specific password variations and common patterns
- **Adaptive Behavior**: Responds to rate limiting and lockout indicators
- **Stop Conditions**: Lockout detection, time limits, or success thresholds

### Target Authentication Systems

#### HTML Form Authentication
- **Target**: `http://192.168.100.101/login.html`
- **Method**: POST to `/dologin.html`
- **Constraint**: Alphanumeric, 8 characters
- **Success Detection**: Redirect to `/success.html` or content analysis

#### HTTP Basic Authentication
- **Target**: `http://192.168.100.103/basicauth`
- **Method**: GET with Authorization header
- **Constraint**: Alphanumeric, 8 characters  
- **Success Detection**: HTTP 200 response code

#### HTTP Digest Authentication
- **Target**: `http://192.168.100.103/digestauth`
- **Method**: GET with Digest authentication
- **Constraint**: Alphanumeric, 6 characters
- **Success Detection**: HTTP 200 response code

## Password Generation Strategy

### Context Tokens
- **General**: Security, Password, Auth, Admin, User
- **Common**: Student, Class, Fall, Spring, Winter, Summer

### Transformation Rules
- **Time-based**: Years 2018-2026, seasons, current academic terms
- **Leetspeak**: Strategic character substitutions (a→@, e→3, o→0)
- **Suffixes**: !, !!, 123, !23, !2024, !2025
- **Case Variations**: Proper capitalization, all caps, all lowercase

### Ranking Algorithm
Candidates are ranked by estimated probability based on:
1. **Length optimization** (6-8 characters prioritized)
2. **Contextual relevance**
3. **Temporal relevance** (current year bonus)
4. **Common patterns** (balanced with novelty)

## Safety & Compliance

### Rate Limiting Controls
- **Base Rate**: ≤2 requests/sec/target
- **Exponential Backoff**: Automatic response to 429/blocking
- **Lockout Detection**: Response time analysis and content inspection
- **Circuit Breaking**: Automatic target suspension on repeated failures

### Ethical Boundaries
- **Approved Scope Only**: Limited to specified lab targets
- **No CAPTCHA Evasion**: Respects interactive security measures
- **No MFA Bypass**: Halts on multi-factor authentication prompts
- **Integrity**: Adherence to ethical hacking principles

### Resource Management
- **CPU-Friendly**: Conservative processing to avoid system stress
- **Memory Efficient**: Streaming data processing where possible
- **Network Respectful**: Rate limiting prevents service disruption

## Analytics & Reporting

### Real-Time Monitoring
- **CSV Logging**: Timestamp, target, username, candidate_id, http_status, response_time, outcome
- **Response Fingerprinting**: Content analysis for authentication state detection
- **Progress Tracking**: Phase transitions and success rate monitoring

### Visualization Charts
*(Note: Visualization scripts are not included in this repository but can be developed separately based on collected data.)*

### Evidence Collection
- **`attack_results.csv`**: Complete attack log with response metadata
- **`successes_redacted.csv`**: Successful authentications (username only)
- **`response_fingerprints.json`**: Authentication state signatures
- **`session_statistics.json`**: Campaign summary and performance metrics

## Usage Instructions

### Basic Execution
```bash
# Generate strategic password candidates
python3 generate_candidates.py
```

### Advanced Configuration
The framework supports customization through direct code modification:
- Modify candidate generation logic in `generate_candidates.py`

## Results Interpretation

### Success Scenarios
- **Password Discovery**: Indicates weak authentication policies
- **Comprehensive Evidence**: Detailed logs support security analysis
- **Pattern Analysis**: Reveals common password trends

### Negative Results (Expected)
- **0% Success Rate**: Demonstrates strong password policies
- **Lockout Detection**: Confirms account protection mechanisms
- **Rate Limiting**: Validates network security controls

Both positive and negative results provide valuable security insights for defensive analysis.

## Technical Requirements

- **Python 3.7+** with requests, pandas, matplotlib, numpy
- **Network Access** to approved lab targets via VPN
- **File System** write permissions for evidence collection
- **Memory**: ~100MB for candidate generation and processing