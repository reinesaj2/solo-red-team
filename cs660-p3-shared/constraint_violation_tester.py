#!/usr/bin/env python3
"""
Constraint Violation Hypothesis Testing
Tests whether the stated constraints (8-char alphanumeric, 6-char alphanumeric) 
are actually correct by testing edge cases and mixed character sets
"""
import string
import random

def generate_constraint_violation_tests():
    """Generate passwords that violate stated constraints to test actual requirements"""
    tests = []
    
    # Test 1: Mixed case (violates "alphanumeric only")
    mixed_case_6 = [
        'WangXx', 'TestAA', 'DemoAA', 'PassWd', 'JmuCsA',
        'Wang01', 'Test01', 'Demo01', 'Pass01', 'User01',
        'WANG01', 'TEST01', 'DEMO01', 'PASS01', 'USER01'
    ]
    
    mixed_case_8 = [
        'WangXxYy', 'TestPass', 'DemoTest', 'Password',
        'Wang2025', 'Test2025', 'Demo2025', 'Pass2025', 
        'WANG2025', 'TEST2025', 'DEMO2025', 'PASS2025',
        'WangTest', 'TestDemo', 'DemoUser', 'UserPass'
    ]
    
    # Test 2: Special characters (violates "alphanumeric only")
    special_6 = [
        'wang@1', 'test@1', 'demo@1', 'pass@1', 'user@1',
        'wang#1', 'test#1', 'demo#1', 'pass#1', 'user#1',
        'wang$1', 'test$1', 'demo$1', 'pass$1', 'user$1',
        'wang!1', 'test!1', 'demo!1', 'pass!1', 'user!1'
    ]
    
    special_8 = [
        'wang@123', 'test@123', 'demo@123', 'pass@123',
        'wang#123', 'test#123', 'demo#123', 'pass#123', 
        'wang$123', 'test$123', 'demo$123', 'pass$123',
        'wang!123', 'test!123', 'demo!123', 'pass!123',
        'password', 'Password', 'PASSWORD', 'passw0rd',
        'P@ssw0rd', 'p@ssw0rd', 'P@SSW0RD', 'Pa$$w0rd'
    ]
    
    # Test 3: Length violations
    short_tests = [
        # Shorter than stated constraint
        'wang', 'test', 'demo', 'pass', 'user',  # 4 chars
        'wang1', 'test1', 'demo1', 'pass1',      # 5 chars  
    ]
    
    long_tests = [
        # Longer than stated constraint
        'wangxxtest', 'testdemouser', 'passwordtest',  # 9+ chars
        'wangxx2025', 'testuser123', 'demopass456',    # 9+ chars
    ]
    
    # Test 4: Academic context specific (real instructor patterns)
    academic_6 = [
        'cs660!', 'jmu660', 'wang22', 'xunhua', 'security',
        'cyber1', 'infosec', 'crypto', 'hash12', 'salt12'
    ]
    
    academic_8 = [
        'cs660fall', 'jmu2025!', 'security', 'wangfall',
        'xunhua25', 'cs660!@#', 'jmucs660', 'fallcs660',
        'Cs660Fall', 'JMU2025!', 'Security', 'Infosec1'
    ]
    
    return {
        'mixed_case_6': mixed_case_6,
        'mixed_case_8': mixed_case_8, 
        'special_6': special_6,
        'special_8': special_8,
        'short_tests': short_tests,
        'long_tests': long_tests,
        'academic_6': academic_6,
        'academic_8': academic_8
    }

def generate_focused_hypothesis_pools():
    """Generate pools based on new hypotheses from failure analysis"""
    
    # Hypothesis 1: Passwords use instructor's actual patterns
    instructor_patterns_6 = [
        'xunhua', 'wang66', 'cs660a', 'jmu660', 'crypto',
        'secur1', 'hash01', 'salt01', 'cipher', 'key123',
        'auth01', 'login1', 'pass66', 'test66', 'demo66'
    ]
    
    instructor_patterns_8 = [
        'xunhua25', 'wang2025', 'cs660fall', 'jmucs660',
        'security', 'cryptoxx', 'hashsalt', 'authpass',
        'loginkey', 'testauth', 'demoauth', 'falltest',
        'springxx', 'project3', 'entity01', 'authenti'
    ]
    
    # Hypothesis 2: Simple dictionary words (English)
    simple_words_6 = [
        'simple', 'secure', 'system', 'access', 'secret',
        'hidden', 'locked', 'opened', 'closed', 'safety'
    ]
    
    simple_words_8 = [
        'password', 'security', 'computer', 'internet', 
        'software', 'hardware', 'database', 'network',
        'firewall', 'antivirus', 'malware', 'spyware'
    ]
    
    # Hypothesis 3: Number-heavy patterns (common in academic settings)
    number_heavy_6 = [
        '123456', '654321', '000000', '111111', '222222',
        '123123', '456456', '789789', '147147', '258258'
    ]
    
    number_heavy_8 = [
        '12345678', '87654321', '00000000', '11111111',
        '12341234', '56785678', '90129012', '19901990',
        '20242024', '20252025', '66006600', '48204820'
    ]
    
    return {
        'instructor_6': instructor_patterns_6,
        'instructor_8': instructor_patterns_8,
        'simple_6': simple_words_6,  
        'simple_8': simple_words_8,
        'numbers_6': number_heavy_6,
        'numbers_8': number_heavy_8
    }

def main():
    """Generate constraint violation and hypothesis test pools"""
    print("Generating constraint violation and focused hypothesis test pools...")
    
    violations = generate_constraint_violation_tests()
    hypotheses = generate_focused_hypothesis_pools()
    
    # Create mixed pools for testing
    # Pool 1: 6-char constraint violations + hypotheses (for Digest)
    digest_test_pool = (
        violations['mixed_case_6'][:10] +
        violations['special_6'][:10] + 
        violations['academic_6'][:10] +
        hypotheses['instructor_6'][:10] +
        hypotheses['simple_6'][:10] +
        hypotheses['numbers_6'][:10]
    )  # 60 total
    
    # Pool 2: 8-char constraint violations + hypotheses (for HTML)
    html_test_pool = (
        violations['mixed_case_8'][:15] +
        violations['special_8'][:15] +
        violations['academic_8'][:15] +
        hypotheses['instructor_8'][:15] +
        hypotheses['simple_8'][:12] +
        hypotheses['numbers_8'][:13]
    )  # 85 total
    
    # Pool 3: 8-char constraint violations + hypotheses (for Basic, different mix)
    basic_test_pool = (
        violations['mixed_case_8'][8:16] +  # Different subset
        violations['special_8'][8:16] +
        violations['short_tests'] +
        violations['long_tests'] +
        hypotheses['instructor_8'][8:] +    # Different subset
        hypotheses['simple_8'][6:] +
        hypotheses['numbers_8'][7:]
    )  # ~70 total
    
    # Save pools
    with open('entropy_pools/digest_constraint_test.txt', 'w') as f:
        f.write('\n'.join(digest_test_pool))
    
    with open('entropy_pools/html_constraint_test.txt', 'w') as f:
        f.write('\n'.join(html_test_pool))
        
    with open('entropy_pools/basic_constraint_test.txt', 'w') as f:
        f.write('\n'.join(basic_test_pool))
    
    print(f"Generated constraint violation test pools:")
    print(f"  Digest (6-char + violations): {len(digest_test_pool)} passwords")
    print(f"  HTML (8-char + violations): {len(html_test_pool)} passwords")  
    print(f"  Basic (8-char + violations): {len(basic_test_pool)} passwords")
    print(f"  Total new test passwords: {len(digest_test_pool) + len(html_test_pool) + len(basic_test_pool)}")
    
    # Show samples
    print(f"\nSample violations for Digest:")
    for i, pwd in enumerate(digest_test_pool[:5]):
        print(f"  {i+1}. {pwd}")
    print(f"\nSample violations for HTML:")
    for i, pwd in enumerate(html_test_pool[:5]):
        print(f"  {i+1}. {pwd}")

if __name__ == "__main__":
    main()