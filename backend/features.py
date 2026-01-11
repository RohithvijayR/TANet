import re
import math
import tldextract
from urllib.parse import urlparse

# Suspicious TLDs often used in phishing
SUSPICIOUS_TLDS = {
    'xyz', 'top', 'gq', 'tk', 'ml', 'cf', 'ga', 'buzz', 'cn', 'ru', 'work', 'date', 'click'
}

def calculate_entropy(text):
    if not text:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(text.count(chr(x))) / len(text)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def is_ip_address(domain):
    # Regex for IPv4
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    return 1 if re.match(ipv4_pattern, domain) else 0

def extract_features(url: str) -> dict:
    # Ensure URL has scheme for proper parsing
    if not url.startswith(('http://', 'https://')):
        url_with_scheme = 'http://' + url
    else:
        url_with_scheme = url
        
    parsed = urlparse(url_with_scheme)
    extracted = tldextract.extract(url)
    
    domain_part = f"{extracted.domain}.{extracted.suffix}"
    full_domain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}".strip('.')
    
    # Structural Features
    features = {
        'url_length': len(url),
        'domain_length': len(full_domain),
        'is_ip': is_ip_address(full_domain),
        'is_https': 1 if parsed.scheme == 'https' else 0,
    }
    
    # Lexical Features (Counts)
    features['count_dot'] = url.count('.')
    features['count_hyphen'] = url.count('-')
    features['count_at'] = url.count('@')
    features['count_question'] = url.count('?')
    features['count_ampersand'] = url.count('&')
    features['count_digits'] = sum(c.isdigit() for c in url)
    
    # Domain Pattern Features
    features['count_subdomain'] = full_domain.count('.') - 1 if not features['is_ip'] else 0
    features['has_suspicious_tld'] = 1 if extracted.suffix in SUSPICIOUS_TLDS else 0
    
    # Entropy (measure of randomness, e.g., dga domains)
    features['domain_entropy'] = calculate_entropy(full_domain)
    
    return features

if __name__ == "__main__":
    # Test
    test_url = "http://paypal.com.account-update.suspicious.xyz/login"
    print(extract_features(test_url))
