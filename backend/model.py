import joblib
import os
import pandas as pd
from features import extract_features
from feedback import FeedbackManager
from logger import TrafficLogger

# Static Allowlist for Top Domains to separate signal from noise
# In production, this would be a bloom filter of Top 1M domains.
TOP_DOMAINS = {
    "google.com", "www.google.com", "youtube.com", "www.youtube.com",
    "facebook.com", "www.facebook.com", "amazon.com", "www.amazon.com",
    "wikipedia.org", "www.wikipedia.org", "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "linkedin.com", "www.linkedin.com", "netflix.com", "www.netflix.com",
    "microsoft.com", "www.microsoft.com", "apple.com", "www.apple.com",
    "github.com", "www.github.com", "gitlab.com", "www.gitlab.com",
    "stackoverflow.com", "www.stackoverflow.com", "reddit.com", "www.reddit.com",
    "bing.com", "www.bing.com", "yahoo.com", "www.yahoo.com",
    "live.com", "www.live.com", "twitch.tv", "www.twitch.tv",
    "discord.com", "www.discord.com", "spotify.com", "www.spotify.com",
    "whatsapp.com", "www.whatsapp.com", "telegram.org", "www.telegram.org",
    "pinterest.com", "www.pinterest.com", "zoom.us", "www.zoom.us",
    "adobe.com", "www.adobe.com", "salesforce.com", "www.salesforce.com",
    "dropbox.com", "www.dropbox.com", "wordpress.com", "www.wordpress.com",
    "cnn.com", "www.cnn.com", "nytimes.com", "www.nytimes.com",
    "bbc.co.uk", "www.bbc.co.uk", "bbc.com", "www.bbc.com",
    "tryhackme.com", "www.tryhackme.com", "firebase.studio", "www.firebase.studio"
}

class PhishingDetector:
    def __init__(self, model_path='model.pkl'):
        # Fix path resolving to be relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(base_dir, model_path)
        self.model = None
        self.feedback = FeedbackManager()
        self.logger = TrafficLogger()
        self.load_model()
        
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"Model loaded from {self.model_path}")
            except Exception as e:
                print(f"Failed to load model: {e}")
                self.model = None
        else:
            print(f"Model file not found at {self.model_path}")
            self.model = None

    def calculate_dynamic_threshold(self, confidence_score):
        """
        AI-based Dynamic Threshold.
        If the model is 99% sure it's phishing, we need more humans to override it.
        If the model is 51% sure, we need fewer humans.
        
        Formula: Base(2) + ScaledConfidence
        Conf 0.5 -> 2 + 0 = 2 votes
        Conf 0.9 -> 2 + 8 = 10 votes
        Conf 0.99 -> 2 + 9 = 11 votes
        """
        # Linear scaling: (confidence - 0.5) * 20
        # 0.5 -> 0
        # 1.0 -> 10
        base_votes = 2
        scaling_factor = int((confidence_score - 0.5) * 20)
        return base_votes + max(0, scaling_factor)

    def scan(self, url: str):
        # 1. Allowlist Check
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'http://' + url)
            hostname = parsed.hostname.lower() if parsed.hostname else ""
            
            # Simple check
            if hostname in TOP_DOMAINS:
                return {
                    "safe": True,
                    "score": 0.0,
                    "reason": "Safe (Popular Domain)"
                }
        except:
            pass

        if not self.model:
            return {"error": "Model not loaded", "safe": False, "score": 1.0}
            
        try:
            features = extract_features(url)
            X = pd.DataFrame([features])
            
            # Predict
            prob = self.model.predict_proba(X)[0][1] # Probability of Class 1 (Phishing)
            is_phishing = prob > 0.5
            
            # Log Data for Retraining
            self.logger.log(url, prob, is_phishing, features)
            
            # 2. Crowd-Sourced Verification Check (Dynamic Threshold)
            if is_phishing:
                safe_votes = self.feedback.get_votes(url)
                required_votes = self.calculate_dynamic_threshold(prob)
                
                if safe_votes >= required_votes:
                    return {
                        "safe": True,
                        "score": prob, # Keep score for debug
                        "reason": f"Verified Safe by Community ({safe_votes} votes override AI suspicion)",
                        "features": features
                    }
            
            # Simple Explanation
            reason = "Safe"
            if is_phishing:
                reason = f"Suspicious URL patterns detected ({prob*100:.1f}% confidence)"
                if features['is_ip']:
                    reason += " (IP address usage)"
                if features['has_suspicious_tld']:
                    reason += " (Suspicious TLD)"
                if features['domain_entropy'] > 4.5:
                    reason += " (High entropy domain)"
                    
            return {
                "safe": not is_phishing, 
                "score": float(prob), 
                "reason": reason,
                "features": features 
            }
        except Exception as e:
            return {"error": str(e), "safe": False, "score": 1.0}
