# Phishing Detection System (PDS)

A privacy-focused, AI-powered browser extension that detects phishing URLs in real-time.

## \ud83d\udee1\ufe0f System Architecture

The system consists of two main components:
1.  **Chrome Extension**: Monitors navigation events and queries the backend. It uses a lightweight decision engine and caching.
2.  **Machine Learning Backend (Python/FastAPI)**: Analyzes URLs using a Random Forest classifier trained on the `PhiUSIIL` dataset. Features are extracted purely from the URL string (structural & lexical), ensuring user privacy (no page content is scraped).

## \ud83d\ude80 Features

-   **Real-time Protection**: Intercepts navigation to malicious sites instantly.
-   **Privacy First**: Only the URL is analyzed. No cookies, session data, or page content is sent to the server.
-   **Explainable AI**: Provides a reason for the block (e.g., "High Entropy Domain", "Suspicious TLD").
-   **Resilient**: Background service worker with local caching for performance.

## \ud83d\udcc1 Prerequisites

-   Python 3.8+
-   Google Chrome (or Brave, Edge, etc.)
-   `pip` (Python package manager)

## \ud83d\udxe0 Installation & Setup

### 1. Backend Setup

1.  Navigate to the project root:
    ```bash
    cd PDS
    ```
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  **Train the Model**:
    The system requires a trained model `model.pkl`. Run the training script (ensure the dataset `PhiUSIIL_Phishing_URL_Dataset.csv` is in the root or configured path):
    ```bash
    python backend/train.py
    ```
5.  **Start the API Server**:
    ```bash
    cd backend
    uvicorn main:app --reload
    ```
    The server will start at `http://localhost:8000`.

### 2. Browser Extension Setup

1.  Open Chrome and navigate to `chrome://extensions`.
2.  Enable **Developer mode** (toggle in the top right corner).
3.  Click **Load unpacked**.
4.  Select the `extension` folder inside this project (`.../PDS/extension`).
    > **Note**: If you see an error about missing icons, run `python generate_icons.py` in the root directory to generate them.

## \ud83d\udd75\ufe0f Usage

1.  Ensure the Backend server is running.
2.  Browse the web as usual.
3.  When you navigate to a website, the extension sends the URL to the backend.
    -   **Safe Sites**: Page loads normally.
    -   **Phishing Sites**: You are redirected to a red warning page.
4.  **Warning Page Options**:
    -   **Go Back**: Returns to the previous safe page.
    -   **Proceed**: Temporarily allows the specific URL (whitelists it for the session).

## \ud83d\udcbb Development

-   **Backend**: Located in `/backend`.
    -   `features.py`: URL feature extraction logic.
    -   `train.py`: Model training pipeline.
    -   `main.py`: API endpoints.
-   **Extension**: Located in `/extension`.
    -   `manifest.json`: V3 Manifest.
    -   `background.js`: Main logic and event listeners.
    -   `interstitial.html/js`: The warning page.

## \u26a0\ufe0f Disclaimer

This tool is a prototype for educational and research purposes. While it uses a high-accuracy model (98%+), no detection system is 100% perfect. Always exercise caution.
