import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from features import extract_features
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.normpath(os.path.join(BASE_DIR, '../PhiUSIIL_Phishing_URL_Dataset.csv'))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')

def load_data(filepath):
    print(f"Loading dataset from {filepath}...")
    # Skipping bad lines if any, though dataset seems clean
    df = pd.read_csv(filepath, on_bad_lines='skip')
    
    # Check expected columns
    if 'URL' not in df.columns or 'label' not in df.columns:
        raise ValueError("Dataset missing 'URL' or 'label' columns")
        
    return df

def prepare_dataset(df):
    print("Extracting features (this may take a while)...")
    
    # Feature Extraction
    features_list = []
    labels = []
    
    # Process a subset if dataset is huge for prototyping, 
    # but let's try full dataset or a reasonable sample (e.g. 10k) to be fast
    # For production-grade, use all. For prototype responsiveness, let's use 20k samples if large.
    if len(df) > 20000:
        print(f"Dataset size {len(df)} is large. Sampling 20,000 for faster training.")
        df = df.sample(20000, random_state=42)
        
    for index, row in df.iterrows():
        try:
            url = str(row['URL'])
            # Label mapping: 0 -> Phishing (1), 1 -> Legitimate (0)
            # Original label: 1=Legit, 0=Phish
            # Target: 1=Phish, 0=Legit
            original_label = int(row['label'])
            target = 1 - original_label 
            
            feats = extract_features(url)
            features_list.append(feats)
            labels.append(target)
        except Exception as e:
            print(f"Error processing URL at index {index}: {e}")
            continue
            
    X = pd.DataFrame(features_list)
    y = np.array(labels)
    
    return X, y

def train_model():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Please ensure file exists.")
        return

    df = load_data(DATASET_PATH)
    X, y = prepare_dataset(df)
    
    print(f"Training on {len(X)} samples with {X.shape[1]} features...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("Model Evaluation:")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(clf, MODEL_PATH)
    print("Done.")

if __name__ == "__main__":
    train_model()
