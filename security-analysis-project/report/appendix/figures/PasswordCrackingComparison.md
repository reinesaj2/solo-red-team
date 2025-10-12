# Password Cracking Comparison Analysis

## Technical Analysis of Password Verification Data Cracking Difficulty

---

## Executive Summary

Systematic password cracking attacks across different systems demonstrate a **dramatic security evolution** in password storage mechanisms. The difficulty levels often create a clear hierarchy, typically moving from older, less secure systems to modern, more robust ones.

This analysis explains the technical causes behind these difficulty differences, focusing on hashing algorithms, salt implementation, and iteration counts.

---

## Technical Analysis of Difficulty Differences

### 1. Legacy System Example: Windows 2003 (LM/NTLM)

**Hash Format**: Dual LM + NTLM storage

**Critical Vulnerabilities (LM Hash):**
1. **No Salt**: Identical passwords produce identical hashes
2. **Case Insensitive**: All passwords converted to uppercase before hashing
3. **14-Character Limit**: Longer passwords truncated
4. **7-Character Splitting**: Password divided into two independent 7-character halves
5. **Weak Algorithm**: DES-based, cryptographically obsolete

#### Mathematical Weakness Example:
```
LM_hash = DES_encrypt("KGS!@#$%", upper(password[0:7])) + DES_encrypt("KGS!@#$%", upper(password[7:14]))
```

**Attack Success**: Rainbow tables provide near-instantaneous lookups
- **Time Complexity**: O(1) table lookup vs. O(n) brute force
- **Coverage**: Precomputed tables can cover a significant portion of the LM password space

### 2. Transitional System Example: Windows 7 (NTLM)

**Hash Format**: NTLM only (LM often disabled by default)

**Security Improvements Over LM:**

#### NTLM Advantages:
1. **Case Sensitive**: Preserves original password case
2. **No Length Limit**: Supports longer passwords
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

**Attack Success**: Dictionary attacks can be highly effective due to common password usage.

### 3. Modern System Example: Linux (SHA-512 crypt)

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
   - **Uniqueness**: Each password gets a random salt
   - **Rainbow Table Prevention**: Makes precomputed tables impractical
   - **Parallel Attack Prevention**: Each hash requires individual computation

2. **Key Stretching (e.g., 5000 iterations)**:
   - **Computational Cost**: Each password test requires multiple hash operations
   - **Time Amplification**: Significantly slower than single-iteration hashes

3. **Strong Hash Algorithm**:
   - **SHA-512**: 512-bit output, cryptographically secure
   - **Collision Resistance**: No known practical attacks
   - **FIPS Approved**: Government-grade cryptographic standard

**Attack Challenges:**
- **Resource Intensive**: Many iterations per password test
- **Salt Uniqueness**: No shared computation benefits

---

## Comparative Security Analysis

### Computational Complexity Comparison (Illustrative)

| System (Example) | Hash Operations Per Password Test | Relative Difficulty |
|------------------|----------------------------------|-------------------|
| **Legacy (LM)** | 0 (table lookup) | 1x (baseline) |
| **Transitional (NTLM)** | 1 MD4 operation | ~5x |
| **Modern (SHA-512 crypt)** | 5000 SHA-512 operations | ~2500x |

### Security Evolution

**Legacy Systems**:
- Often include backward compatibility with older, weaker hashing algorithms.
- Security may be sacrificed for legacy support.

**Transitional Systems**:
- May disable the weakest legacy hashes by default but retain others for compatibility.
- Balance security and performance.

**Modern Systems**:
- Employ modern cryptographic design principles.
- Security-first approach, incorporating lessons from password cracking evolution.

---

## Conclusion

The dramatic difficulty differences between various systems illustrate the evolution of password security:

- **Legacy systems** represent older security practices with fundamental design flaws.
- **Transitional systems** show improvement but may retain vulnerabilities for compatibility.
- **Modern systems** demonstrate current cryptographic best practices.

**Key Insight**: Even with identical passwords, the underlying hash implementation determines attack feasibility. Strong password hashing can make previously vulnerable passwords practically uncrackable, while weak hashing makes even complex passwords vulnerable to rapid attack.

This analysis reinforces the critical importance of **modern password hashing standards** and the security risks inherent in maintaining legacy authentication systems.