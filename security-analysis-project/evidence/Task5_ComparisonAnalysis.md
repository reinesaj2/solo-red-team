# Task 5: Comparison of Three PVD Cracking (5 points)

## CS 660 Project 3: Technical Analysis of Password Verification Data Cracking Difficulty

---

## Executive Summary

Our systematic password cracking attacks across three different systems demonstrate a **dramatic security evolution** from Windows 2003 to Linux systems. The difficulty levels create a clear hierarchy:

**Windows 2003 (Easiest)** → **Windows 7 (Moderate)** → **Linux Ubuntu (Hardest)**

This analysis explains the technical causes behind these difficulty differences, focusing on hashing algorithms, salt implementation, and iteration counts.

---

## Attack Results Summary

| System | Hash Type | Success Rate | Primary Tool | Attack Time | Key Weakness Exploited |
|--------|-----------|--------------|--------------|-------------|----------------------|
| **Windows 2003** | LM + NTLM | 60% (9/15) | Ophcrack | 2m 22s | LM rainbow tables |
| **Windows 7** | NTLM only | 86% (6/7) | John the Ripper | 3 seconds | Dictionary attack |
| **Linux Ubuntu** | SHA-512 crypt | 37.5% (3/8) | John the Ripper | 8 minutes | Password reuse patterns |

---

## Technical Analysis of Difficulty Differences

### 1. Windows 2003: The Weakest Link

**Hash Format**: Dual LM + NTLM storage
- **LM Hash**: `DB170C426EAE78BEFF17365FAF1FFE89` (Morpheus example)
- **NTLM Hash**: `482563F0ADAAC6CA60C960C0199559D2` (Morpheus example)

**Critical Vulnerabilities:**

#### LM Hash Fundamental Flaws:
1. **No Salt**: Identical passwords produce identical hashes
2. **Case Insensitive**: All passwords converted to uppercase before hashing
3. **14-Character Limit**: Longer passwords truncated
4. **7-Character Splitting**: Password divided into two independent 7-character halves
5. **Weak Algorithm**: DES-based, cryptographically obsolete

#### Mathematical Weakness:
```
LM_hash = DES_encrypt("KGS!@#$%", upper(password[0:7])) + DES_encrypt("KGS!@#$%", upper(password[7:14]))
```

**Attack Success**: Rainbow tables provide near-instantaneous lookups
- **Time Complexity**: O(1) table lookup vs. O(n) brute force
- **Coverage**: XP free small tables cover ~99.95% of LM password space
- **Result**: 60% success in 2 minutes 22 seconds despite incomplete table set

### 2. Windows 7: Moderate Difficulty (Major Security Improvement)

**Hash Format**: NTLM only (LM disabled by default)
- **NTLM Hash**: `482563f0adaac6ca60c960c0199559d2` (Morpheus example)

**Security Improvements Over LM:**

#### NTLM Advantages:
1. **Case Sensitive**: Preserves original password case
2. **No Length Limit**: Supports passwords up to 256 characters
3. **Unicode Support**: Full character set support
4. **No Splitting**: Single hash for entire password

#### NTLM Algorithm:
```
NTLM_hash = MD4(UTF-16LE(password))
```

**Remaining Vulnerabilities:**
1. **No Salt**: Identical passwords still produce identical hashes
2. **Single Iteration**: No key stretching (computational cost = 1 MD4 operation)
3. **Fast Algorithm**: MD4 allows rapid brute force attacks

**Attack Success**: Dictionary attacks highly effective
- **Primary Success Factor**: Common password usage
- **Result**: 86% success in 3 seconds using rockyou dictionary
- **Resource Impact**: Minimal CPU usage, no overheating concerns

### 3. Linux Ubuntu: Maximum Security (SHA-512 crypt)

**Hash Format**: SHA-512 with salt and iterations
- **Example**: `$6$ykumbyCz$IiKc0RFh2Xa/uV9H8Ayed9aHSSAPEWx0LI8GMtaGrJX61iuYa2Qdw.8rt2bxnZPZgBqm2To26K7a/YDfbTsY61`

**Security Components:**

#### Format Breakdown:
- `$6$`: Algorithm identifier (SHA-512)
- `ykumbyCz`: 8-character random salt
- `IiKc0RFh...`: Base64-encoded hash result (86 characters)

#### SHA-512 crypt Algorithm:
```
hash = SHA-512^5000(password + salt + additional_data)
```

**Advanced Security Features:**

1. **Cryptographic Salt**:
   - **Uniqueness**: Each password gets random 8-character salt
   - **Rainbow Table Prevention**: Makes precomputed tables impractical
   - **Parallel Attack Prevention**: Each hash requires individual computation

2. **Key Stretching (5000 iterations)**:
   - **Computational Cost**: Each password test requires 5000 SHA-512 operations
   - **Time Amplification**: 5000x slower than single-iteration hashes
   - **Mathematical Impact**: Attack time increases linearly with iteration count

3. **Strong Hash Algorithm**:
   - **SHA-512**: 512-bit output, cryptographically secure
   - **Collision Resistance**: No known practical attacks
   - **FIPS Approved**: Government-grade cryptographic standard

**Attack Challenges:**
- **Resource Intensive**: 5000 iterations per password test
- **Salt Uniqueness**: No shared computation benefits
- **Limited Success**: Only succeeded with password reuse patterns (37.5%)

---

## Comparative Security Analysis

### Computational Complexity Comparison

| System | Hash Operations Per Password Test | Time per 1M Tests | Relative Difficulty |
|--------|----------------------------------|------------------|-------------------|
| **LM (rainbow table)** | 0 (table lookup) | <1 second | 1x (baseline) |
| **NTLM** | 1 MD4 operation | ~5 seconds | 5x |
| **SHA-512 crypt** | 5000 SHA-512 operations | ~2500 seconds | 2500x |

### Security Evolution Timeline

**Windows 2003 (2003)**:
- Backward compatibility with LM (1980s technology)
- Security sacrificed for legacy support
- No consideration for rainbow table attacks

**Windows 7 (2009)**:
- LM disabled by default (major improvement)
- NTLM retained for compatibility
- Balances security and performance

**Linux SHA-512 crypt (2008+)**:
- Modern cryptographic design
- Security-first approach
- Incorporates lessons from password cracking evolution

---

## Strategic Attack Implications

### Weakest Link Principle Validation

Our results perfectly demonstrate the **weakest link security principle**:

1. **Windows 2003**: LM hashes provided the easiest entry point
2. **Windows 7**: Unsalted NTLM hashes vulnerable to dictionary attacks
3. **Linux**: Strong hashing forced reliance on password reuse patterns

### Resource Optimization

**Attack Efficiency (ROI Analysis)**:
- Windows 2003: **Highest ROI** - 60% success in 2.4 minutes
- Windows 7: **Medium ROI** - 86% success in 3 seconds  
- Linux: **Lowest ROI** - 37.5% success in 8 minutes

### Modern Security Lessons

1. **Salt Necessity**: Prevents rainbow table attacks and parallel processing
2. **Iteration Count Importance**: Key stretching dramatically increases attack cost
3. **Algorithm Selection**: Modern hash functions resist cryptographic attacks
4. **Legacy Danger**: Backward compatibility can create security vulnerabilities

---

## Conclusion

The dramatic difficulty differences between these systems illustrate **30 years of password security evolution**:

- **Windows 2003** represents legacy security with fundamental design flaws
- **Windows 7** shows transitional improvement with remaining vulnerabilities  
- **Linux SHA-512** demonstrates modern cryptographic best practices

**Key Insight**: Even with identical passwords, the underlying hash implementation determines attack feasibility. Strong password hashing can make previously vulnerable passwords practically uncrackable, while weak hashing makes even complex passwords vulnerable to rapid attack.

This analysis reinforces the critical importance of **modern password hashing standards** and the security risks inherent in maintaining legacy authentication systems.