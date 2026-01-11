from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model import PhishingDetector

app = FastAPI(title="Phishing Detection API")

# Enable CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = PhishingDetector()

class URLRequest(BaseModel):
    url: str

class ReportRequest(BaseModel):
    url: str
    vote: str = "safe"

@app.post("/scan")
def scan_url(request: URLRequest):
    result = detector.scan(request.url)
    if "error" in result:
        if result["error"] == "Model not loaded":
             return {"safe": True, "score": 0.0, "reason": "System initializing (Model not ready)"}
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/report")
def report_url(request: ReportRequest):
    # 1. Update allowlist/blocklist counts
    if request.vote == "safe":
        new_count = detector.feedback.add_report(request.url)
    
    # 2. Extract features to save rich data for training
    features = {}
    try:
        from features import extract_features
        features = extract_features(request.url)
    except:
        pass

    # 3. Log to user_reports.csv
    # Vote 'safe' -> Label 0
    # Vote 'unsafe' -> Label 1
    label = 0 if request.vote == "safe" else 1
    detector.logger.log_user_report(request.url, label, features)

    return {"status": "recorded", "vote": request.vote}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": detector.model is not None}
