# Task 1: Tool Study (5 points)

## CS 660 Project 3: Security Tool Analysis

This document provides detailed analysis of the three primary password cracking tools used in this project, explaining how each works and their respective advantages.

---

## 1. Ophcrack (2 points)

### How Ophcrack Works

**Core Technology: Rainbow Tables**
- Ophcrack uses precomputed rainbow tables to perform time-memory trade-off attacks
- Rainbow tables contain chains of hash-to-plaintext mappings that cover large password spaces
- Instead of computing hashes in real-time, Ophcrack looks up precomputed results

**Attack Process:**
1. **Table Selection**: Choose appropriate tables (e.g., XP free small, Vista free)
2. **Hash Lookup**: Search target hash in rainbow table chains
3. **Chain Walking**: If hash found in chain, reconstruct the plaintext password
4. **Verification**: Confirm password by hashing and comparing to target

**LM Hash Specialization:**
- Particularly effective against LM hashes due to their structural weaknesses
- LM passwords are split into 7-character halves, each cracked independently
- Case-insensitive nature reduces keyspace significantly
- 14-character limit makes complete coverage feasible

### Advantages over John the Ripper and Hashcat

1. **Speed**: Near-instantaneous lookups when hash exists in tables
   - Our results: 9/15 Windows 2003 LM passwords in 2 minutes 22 seconds
   - No computational overhead during actual cracking phase

2. **LM Hash Optimization**: Purpose-built for Windows LM hash weaknesses
   - Exploits case-insensitive nature and 7-character splitting
   - Comprehensive coverage of LM password space with appropriate tables

3. **Predictable Success**: Known coverage percentage for given table sets
   - XP free small tables: ~99.95% success rate with complete set
   - Deterministic results - if password is in table, it WILL be found

4. **Resource Efficiency**: Minimal CPU usage during lookups
   - Primary resource requirement is disk space for tables
   - No intensive computational processes during cracking

**Disadvantages:**
- Requires significant storage space for comprehensive tables
- Limited to hash types with available rainbow tables
- Ineffective against salted hashes (tables become impractical)

---

## 2. John the Ripper (1 point)

### How John the Ripper Works

**Core Technology: Multi-Attack Password Cracking**
- John is a versatile password cracker supporting multiple attack modes and hash formats
- Uses CPU-based computation to test password candidates against target hashes
- Supports over 400 hash formats including LM, NTLM, Unix crypt, and modern formats

**Attack Modes:**
1. **Dictionary Attack**: Tests passwords from wordlists (e.g., rockyou.txt)
2. **Rules-Based Attack**: Applies transformation rules to dictionary words (e.g., append numbers)
3. **Incremental Attack**: Systematic brute force using character sets
4. **External Mode**: Custom attack modes using C-like programming language

**Process Flow:**
1. **Hash Detection**: Automatically identify hash format from input
2. **Candidate Generation**: Create password candidates based on selected mode
3. **Hash Computation**: Calculate hash for each candidate
4. **Comparison**: Compare computed hash with target hash
5. **Success Recording**: Store successful password matches

### Advantages over Ophcrack and Hashcat

1. **Format Versatility**: Supports the widest range of hash formats
   - 400+ formats vs. Ophcrack's LM/NTLM focus
   - Includes modern formats like bcrypt, scrypt, Argon2

2. **Attack Method Flexibility**: Multiple complementary attack approaches
   - Dictionary, rules, incremental, external modes
   - Can adapt strategy based on target characteristics

3. **Resource Scalability**: Efficient CPU utilization without GPU requirements
   - Works effectively on any system with decent CPU
   - No special hardware dependencies

4. **Incremental Intelligence**: Smart brute force with optimized character ordering
   - Prioritizes common character patterns
   - More efficient than pure brute force approaches

**Results in Our Testing:**
- Windows 7 NTLM: 6/7 passwords in under 10 minutes
- Primary success from dictionary attack in 3 seconds
- Excellent ROI for unsalted hash formats

---

## 3. Hashcat (2 points)

### How Hashcat Works

**Core Technology: GPU-Accelerated Password Cracking**
- Hashcat leverages Graphics Processing Units (GPUs) for massively parallel hash computation
- Uses CUDA (NVIDIA) or OpenCL (AMD/Intel) to distribute workload across GPU cores
- Modern GPUs can perform billions of hash computations per second

**Architecture:**
1. **Parallel Processing**: Distributes password candidates across hundreds/thousands of GPU cores
2. **Memory Management**: Efficiently manages GPU memory for hash targets and candidates
3. **Optimization**: Uses GPU-specific optimizations for different hash algorithms
4. **Multi-Device**: Can utilize multiple GPUs simultaneously

**Attack Capabilities:**
- Dictionary attacks with massive parallelization
- Rule-based attacks with GPU-optimized transformations
- Mask attacks (targeted brute force with patterns)
- Hybrid attacks combining multiple methods
- Supports 300+ hash algorithms

### Advantages over Ophcrack and John the Ripper

1. **Raw Computational Power**: Orders of magnitude faster hash computation
   - Modern GPUs: 10-100+ billion MD5 hashes per second
   - John the Ripper (CPU): Millions to low billions per second
   - Ophcrack: Lookup speed but limited to table contents

2. **Brute Force Feasibility**: Makes previously infeasible attacks practical
   - Can brute force 8-character passwords in reasonable time
   - Complex rule sets applied to large dictionaries become viable

3. **Modern Hash Support**: Optimized for contemporary hash algorithms
   - Efficient implementations of bcrypt, scrypt, Argon2
   - Better performance on resource-intensive modern hashes than CPU-based tools

4. **Scalability**: Linear performance improvement with additional GPUs
   - Can build multi-GPU rigs for extreme performance
   - Professional password recovery operations often use Hashcat clusters

**Technical Advantages:**
- **Memory Bandwidth**: GPU memory bandwidth (500+ GB/s) vs. CPU (50-100 GB/s)
- **Core Count**: 2000+ GPU cores vs. 4-16 CPU cores
- **Specialized Architecture**: Designed for parallel mathematical operations

**Limitations:**
- **Hardware Dependency**: Requires compatible GPU hardware
- **Power Consumption**: High electrical power requirements
- **Heat Generation**: Significant thermal management needs
- **Virtual Machine Incompatibility**: Cannot run effectively in VMs

---

## Summary Comparison

| Tool | Best Use Case | Primary Strength | Speed | Resource Requirements |
|------|---------------|------------------|-------|---------------------|
| **Ophcrack** | LM hashes, instant results | Rainbow table lookups | Fastest (when hash in table) | Disk space |
| **John the Ripper** | Versatility, CPU systems | Format support & flexibility | Moderate | CPU cycles |
| **Hashcat** | GPU systems, brute force | Raw computational power | Fastest (computational) | GPU hardware |

## Strategic Application in CS 660 Project

Our project demonstrates the **weakest link principle** perfectly:

1. **Ophcrack** → Windows 2003 LM hashes → 2 minutes 22 seconds
2. **John the Ripper** → Windows 7 NTLM hashes → 3 seconds (dictionary)
3. **John the Ripper** → Linux SHA-512 hashes → [To be determined]

Each tool has optimal use cases, and understanding their strengths enables efficient strategic password recovery operations while maintaining reasonable resource consumption.