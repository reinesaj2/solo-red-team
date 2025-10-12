# Security Analysis Project Checklist

## Prerequisites and Preparation

### System Analysis
- [x] **Analyze Windows 7 PVD file**
  - [x] Understand every field in every line
  - [x] Document field meanings and separators
- [x] **Analyze Windows 2003 PVD file**
  - [x] Understand every field in every line
  - [x] Document field meanings and separators
- [x] **Analyze Linux PVD file**
  - [x] Understand every field in every line
  - [x] Document field meanings and separators
- [x] **Weakest link analysis** (before any tool usage)
  - [x] Perform feasibility calculations
  - [x] Identify most vulnerable authentication method
  - [x] Document rationale for attack priority order
- [x] **Resource Monitoring**
  - [x] Monitor system resources during attacks
  - [x] Stop if excessive heat/resource usage detected

### Theoretical Foundations
- [x] **Explain role of one-wayness in password hashing**
- [x] **Explain role of salt in password hashing**
- [x] **Explain role of iteration count in password hashing**
- [x] **Understand mathematical notation: v = h^50,000(w||s)**
  - [x] h = cryptographic hash function
  - [x] w = password
  - [x] s = random salt
  - [x] 50,000 = iteration count
- [x] **Explain LM password hash generation process**
- [x] **Explain NTLM password hash generation process**
- [x] **Explain Linux password hash generation process**

### Security Tools Setup
- [x] **Install and configure Ophcrack**
  - [x] Download rainbow tables
  - [x] Verify table integrity
- [x] **Install John the Ripper**
  - [x] Review examples
  - [x] Test basic functionality
- [x] **Install Hydra** (if needed for online attacks)
  - [x] Test basic functionality
  - [x] Document version number: Hydra v9.5
- [ ] **Consider Hashcat** (only if hardware GPU available)
  - [ ] Verify GPU support
  - [ ] Install and test if applicable

## PVD File Study

### Windows 7 PVD Analysis
- [x] **Obtain PVD file**
- [x] **Find target line and analyze**
  - [x] (a) Explain what each non-empty field is (fields separated by ":")
  - [x] (b) Count password hash values in the line
  - [x] (c) Check uniqueness of each hash vs. other hashes in file
    - [x] Document meaning if not unique

### Windows 2003 PVD Analysis
- [x] **Obtain PVD file**
- [x] **Find target line and analyze**
  - [x] (a) Explain what each non-empty field is (fields separated by ":")
  - [x] (b) Count password hash values in the line
  - [x] (c) Check uniqueness of each hash vs. other hashes in file
    - [x] Document meaning if not unique

### Ubuntu PVD Analysis
- [x] **Obtain PVD file**
- [x] **Find target line and analyze**
  - [x] (a) Explain what each non-empty field is (fields separated by ":")
  - [x] (b) Explain parts separated by "$" within fields
    - [x] Document meaning of each $-separated component

## Tool Study

### Ophcrack Analysis
- [x] **How does Ophcrack work?**
- [x] **What are its advantages over John the Ripper and Hashcat?**

### John the Ripper Analysis
- [x] **How does John the Ripper work?**
- [x] **What are its advantages over Ophcrack and Hashcat?**

### Hashcat Analysis
- [x] **How does Hashcat work?**
- [x] **What are its advantages over Ophcrack and John the Ripper?**

## Windows 7 Password Cracking

### Target Users
- [x] **Morpheus** - Password: a1b2c3d4 | Tool: john --format=NT (dictionary) | Runtime: 3 seconds
- [x] **Neo** - Password: qwerty10 | Tool: john --format=NT (dictionary) | Runtime: 3 seconds
- [x] **Trinity** - Password: letmein2 | Tool: john --format=NT (dictionary) | Runtime: 3 seconds
- [x] **Cypher** - Password: passw0rd | Tool: john --format=NT (dictionary) | Runtime: 3 seconds
- [x] **Smith** - Password: qaZwsX | Tool: john --format=NT (jumbo rules) | Runtime: 6 seconds
- [x] **Cobb** - Password: 1q2w3e4r | Tool: john --format=NT (dictionary) | Runtime: 3 seconds
- [x] **Arthur** - Password: trustno1 | Tool: john --format=NT (dictionary) | Runtime: 3 seconds

## Windows 2003 Password Cracking

### Primary Target Users
- [x] **Administrator** - Password: mskitty666 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Morpheus** - Password: a1b2c3d4 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Neo** - Password: qwerty10 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Trinity** - Password: letmein2 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Cypher** - Password: passw0rd | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Smith** - Password: qaZwsX | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Cobb** - Password: 1q2w3e4r | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s
- [x] **Arthur** - Password: trustno1 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 22s

### Optional Service Accounts
- [x] **ASPNET** - Password: D5912K8 | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 2s
- [ ] **IUSR_JAMES-BFCF5F2D5** - Password: NOT CRACKED | Tool: ophcrack-cli (needs larger tables) | Runtime: 2m 2s
- [ ] **IWAM_JAMES-BFCF5F2D5** - Password: NOT CRACKED | Tool: ophcrack-cli (needs larger tables) | Runtime: 2m 2s
- [ ] **SUPPORT_388945a0** - Password: NOT IN FILE | Tool: N/A | Runtime: N/A
- [x] **System32** - Password: ABB1T | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 2s
- [x] **SYS_32** - Password: ABB1T | Tool: ophcrack-cli (LM rainbow tables) | Runtime: 2m 2s

## Linux Password Cracking

### Target Users
- [x] **Morpheus** - Password: A1B2C3D4 | Tool: john --format=sha512crypt (enhanced wordlist + best64 rules) | Runtime: 7 seconds
- [x] **Neo** - Password: Qwerty10 | Tool: john --format=sha512crypt (enhanced wordlist + best64 rules) | Runtime: 7 seconds  
- [x] **Trinity** - Password: LetMeIn2 | Tool: john --format=sha512crypt (strategic case variations) | Runtime: <1 minute
- [x] **Cypher** - Password: Passw0rd | Tool: john --format=sha512crypt (enhanced wordlist) | Runtime: <1 minute
- [x] **Smith** - Password: QazWsx | Tool: john --format=sha512crypt (strategic case variations) | Runtime: <1 minute
- [x] **Cobb** - Password: 1Q2w3e4R | Tool: john --format=sha512crypt (strategic case variations) | Runtime: <1 minute
- [x] **Arthur** - Password: trustNo1 | Tool: john --format=sha512crypt (strategic case variations) | Runtime: <1 minute

### Bonus Target
- [ ] **root** - Password: NOT CRACKED | Tool: john --format=sha512crypt | Runtime: 15 minutes (strategic approaches) - Demonstrates strong security!

## PVD Cracking Comparison

- [x] **Compare difficulty levels of Windows 7, Windows 2003, and Ubuntu PVD cracking**
- [x] **Explain technical causes of differences**
  - [x] Hashing algorithms used
  - [x] Salt implementation and effectiveness
  - [x] Iteration count differences
  - [x] Impact on attack feasibility
- [x] **Provide detailed technical analysis**

## Online Password Guessing

### VPN Setup
- [x] **Configure VPN connection**
- [x] **Verify internal IP assignment** (e.g., 192.168.101.10)
- [x] **Test connectivity to target machines**
  - [x] ping 192.168.100.101
  - [x] ping 192.168.100.103

### HTML-based Authentication Cracking
- [x] **Target**: http://192.168.100.101/login.html
- [x] **Username**: wangxx
- [x] **Password constraints**: alphanumeric, 8 characters
- [x] **Test with known credentials**: test/test
- [x] **Download password dictionary**
- [x] **Filter dictionary to 8-character passwords**
- [x] **Configure and run Hydra attack**
  - [x] Document Hydra version: v9.5
  - [x] Record successful password: tripsine | Tool: hydra distributed attack (partition ae) | Runtime: ~2 hours distributed
  - [x] Document runtime: Multiple tests, rate-limited to 6-12 attempts/minute
  - [x] Record exact commands used: See COMMANDS.log for complete history

### HTTP Basic Authentication Cracking
- [x] **Target**: http://192.168.100.103/basicauth
- [x] **Username**: wangxx
- [x] **Password constraints**: alphanumeric, 8 characters
- [x] **Download and prepare password dictionary**
- [x] **Configure and run Hydra attack**
  - [x] Document Hydra version: v9.5
  - [x] Record successful password: sotalait | Tool: hydra distributed attack (partition ag) | Runtime: ~2 hours distributed
  - [x] Document runtime: Distributed attack across 16 partitions with 124 concurrent processes
  - [x] Record exact commands used: See COMMANDS.log for complete history
- [x] **Access protected page and document content** - SUCCESS - Password "sotalait" discovered via distributed Hydra attack

### HTTP Digest Authentication Cracking
- [x] **Target**: http://192.168.100.103/digestauth
- [x] **Username**: wangxx
- [x] **Password constraints**: alphanumeric, 6 characters (NOT 8!)
- [x] **Download and prepare password dictionary**
- [x] **Filter dictionary to 6-character passwords**
- [x] **Configure and run Hydra attack**
  - [x] Document Hydra version: v9.5
  - [x] Record successful password: hakkis | Tool: hydra distributed 32-part attack (partition 18) | Runtime: ~6 hours distributed
  - [x] Document runtime: 32-way parallel attack across 6-character wordlist (341,025 passwords)
  - [x] Record exact commands used: See COMMANDS.log for complete history
- [x] **Access protected page and document content** - SUCCESS - Password "hakkis" discovered via 32-partition distributed Hydra attack

## Token-based Authentication

### RSA Algorithm Review
- [x] **RSA public key components**: (N,e)
- [x] **RSA private key components**: d
- [x] **Chinese Remainder Theorem optimization** (optional)
  - [x] d mod (p-1), d mod (q-1), q^-1 mod p
  - [x] Garner's formula

### Certificate and Key Analysis
- [x] **RSA public key (e,c)**: e=65537, N=009ed0770fdb3f97...
- [x] **RSA private key d**: 11fc4ddf8fd6edc9eeb1e8c0...
- [x] **Full name in certificate**: C=US, ST=Virginia, L=Harrisonburg, O=JMU, OU=CS, CN=Abraham Reines 2025-660
- [x] **CA's full name**: C=US, ST=Virginia, L=Harrisonburg, O=JMU, OU=CS, CN=Xunhua 2024 CA
- [x] **CA key identifier**: 07:39:37:A2:BB:D4:94:B4:F0:8D:42:27:BB:50:45:25:52:DF:BB:2D
