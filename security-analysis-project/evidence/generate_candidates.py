#!/usr/bin/env python3
"""
Password Candidate Generator for Security Testing
Generates context-aware password candidates ranked by probability
"""

import itertools
import random
from collections import defaultdict
import re

class PasswordCandidateGenerator:
    def __init__(self):
        # Core organizational tokens (can be customized for specific targets)
        self.org_tokens = [
            "Company", "company", "Org", "org", "Admin", "admin",
            "Secure", "secure", "Security", "security"
        ]
        
        # IT default passwords
        self.it_defaults = [
            "Welcome", "welcome", "WELCOME",
            "ChangeMe", "changeme", "CHANGEME", 
            "Temp", "temp", "TEMP",
            "Password", "password", "PASSWORD"
        ]
        
        # Time-based tokens
        self.years = [str(y) for y in range(2018, 2027)]
        self.short_years = [str(y)[2:] for y in range(2018, 2027)]
        self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.seasons = ["Fall", "Spring", "Summer", "Winter"]
        
        # Specified suffixes
        self.suffixes = ["!", "!!", "123", "!23", "!2024", "!2025"] # Added !2025 for current year
        
        # Leetspeak transformations (a,e,i,o,s,t only as specified)
        self.leet_map = {
            'a': ['a', '@', '4'],
            'e': ['e', '3'],
            'i': ['i', '1'],
            'o': ['o', '0'],
            's': ['s', '$', '5'],
            't': ['t', '7']
        }
        
    def apply_leetspeak(self, word, intensity=0.3):
        """Apply leetspeak transformations with given intensity"""
        result = []
        for char in word.lower():
            if char in self.leet_map and random.random() < intensity:
                result.append(random.choice(self.leet_map[char]))
            else:
                result.append(char)
        return ''.join(result)
    
    def generate_base_candidates(self):
        """Generate base password candidates using specified combinatorial patterns"""
        candidates = set()
        
        # Base tokens and IT defaults
        all_tokens = self.org_tokens + self.it_defaults
        candidates.update(all_tokens)
        
        # Combinator 1: {token}{year}
        for token in all_tokens:
            for year in self.years + self.short_years:
                candidates.add(f"{token}{year}")
        
        # Combinator 2: {token}{suffix}
        for token in all_tokens:
            for suffix in self.suffixes:
                candidates.add(f"{token}{suffix}")
        
        # Combinator 3: {Month}{Year}
        for month in self.months:
            for year in self.years + self.short_years:
                candidates.add(f"{month}{year}")
        
        # Combinator 4: {Season}{Year}
        for season in self.seasons:
            for year in self.years + self.short_years:
                candidates.add(f"{season}{year}")
        
        return list(candidates)
    
    def apply_transformations(self, base_candidates):
        """Apply case variations and leetspeak transformations"""
        transformed = set()
        
        for candidate in base_candidates:
            # Original
            transformed.add(candidate)
            
            # Case variations
            transformed.add(candidate.upper())
            transformed.add(candidate.lower())
            transformed.add(candidate.capitalize())
            
            # Leetspeak variations for a,e,i,o,s,t
            leet_versions = self.generate_leet_variations(candidate)
            transformed.update(leet_versions)
        
        return list(transformed)
    
    def generate_leet_variations(self, word):
        """Generate all leetspeak variations for specified characters"""
        variations = set()
        
        # Generate combinations of leet substitutions
        def generate_leet_combos(text, pos=0):
            if pos >= len(text):
                variations.add(text)
                return
            
            char = text[pos].lower()
            if char in self.leet_map:
                for replacement in self.leet_map[char]:
                    new_text = text[:pos] + replacement + text[pos+1:]
                    generate_leet_combos(new_text, pos + 1)
            else:
                generate_leet_combos(text, pos + 1)
        
        # Generate with original case
        generate_leet_combos(word)
        
        # Also generate with different case variations of leet versions
        temp_variations = list(variations)
        for var in temp_variations:
            variations.add(var.upper())
            variations.add(var.lower()) 
            variations.add(var.capitalize())
        
        return variations
    
    def rank_candidates(self, candidates):
        """Rank candidates by estimated probability based on general patterns"""
        scores = defaultdict(int)
        
        for candidate in candidates:
            score = 0
            lower_candidate = candidate.lower()
            
            # Length scoring (favor 6-8 characters based on common password policies)
            if 6 <= len(candidate) <= 8:
                score += 100
            elif len(candidate) == 5 or len(candidate) == 9:
                score += 50
            elif len(candidate) == 4 or len(candidate) == 10:
                score += 25
            
            # Contextual relevance (general terms)
            if any(term in lower_candidate for term in ["company", "admin", "security", "password", "login"]):
                score += 150
            
            # Current year bonus (adjust as needed for current year)
            if any(year in candidate for year in ["2024", "2025", "24", "25"]):
                score += 80
            
            # Common patterns
            if any(pattern in lower_candidate for pattern in ["123", "password", "welcome", "qwerty"]):
                score += 60
            
            # Proper capitalization (more likely to be used)
            if candidate and candidate[0].isupper() and candidate[1:].islower(): # Added check for empty string
                score += 40
            
            # Has numbers (common in passwords)
            if any(c.isdigit() for c in candidate):
                score += 30
            
            # Special characters
            if any(c in "!@#$%^&*()" for c in candidate):
                score += 20
            
            # Penalty for very common patterns (likely already tried)
            if lower_candidate in ["password", "123456", "qwerty", "welcome"]:
                score -= 50
            
            scores[candidate] = score
        
        # Sort by score (highest first) and return
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [candidate for candidate, score in ranked]
    
    def generate_top_candidates(self, limit=10000):
        """Generate and return top N password candidates"""
        print("Generating base candidates...")
        base_candidates = self.generate_base_candidates()
        print(f"Generated {len(base_candidates)} base candidates")
        
        print("Applying transformations...")
        all_candidates = self.apply_transformations(base_candidates)
        print(f"Generated {len(all_candidates)} total candidates after transformations")
        
        print("Ranking candidates...")
        ranked_candidates = self.rank_candidates(all_candidates)
        
        # Filter for reasonable lengths and characters
        filtered_candidates = []
        for candidate in ranked_candidates:
            if 4 <= len(candidate) <= 12 and candidate.isprintable():
                filtered_candidates.append(candidate)
                if len(filtered_candidates) >= limit:
                    break
        
        return filtered_candidates[:limit]

def main():
    """Generate strategic password candidates for security testing"""
    generator = PasswordCandidateGenerator()
    
    print("Password Candidate Generator")
    print("=" * 50)
    
    # Generate candidates
    candidates = generator.generate_top_candidates(10000)
    
    # Write to file
    output_file = "candidates.txt" # Changed to a relative path
    with open(output_file, 'w') as f:
        for candidate in candidates:
            f.write(f"{candidate}\n")
    
    print(f"Generated {len(candidates)} strategic password candidates")
    print(f"Saved to: {output_file}")
    print("\nTop 20 candidates:")
    for i, candidate in enumerate(candidates[:20], 1):
        print(f"{i:2d}: {candidate}")
    
    print(f"\nCandidate distribution by length:")
    length_dist = defaultdict(int)
    for candidate in candidates:
        length_dist[len(candidate)] += 1
    
    for length in sorted(length_dist.keys()):
        print(f"  {length} chars: {length_dist[length]} candidates")

if __name__ == "__main__":
    main()
