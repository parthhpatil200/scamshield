from pathlib import Path

from joblib import load
from scipy.sparse import csr_matrix, hstack
from .preprocessing import clean_text
from .flags import detect_scam_flags
from .risk_engine import compute_risk_score
from .explanation import generate_explanation
from .scam_patterns import extract_features_batch, extract_scam_features

# Load trained artifacts once
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODELS_DIR / "scam_model_xgb.pkl"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.pkl"

model = load(MODEL_PATH)
vectorizer = load(VECTORIZER_PATH)


def analyze_text(text: str) -> dict:
    """
    Full ScamShield inference pipeline.
    """

    # 1) Clean text
    cleaned_text = clean_text(text)

    # 2) Transform text with TF-IDF vectorizer
    tfidf_features = vectorizer.transform([cleaned_text])

    # 3) Extract scam pattern features
    detected_scam_features = extract_scam_features(cleaned_text)
    pattern_features = csr_matrix(extract_features_batch([cleaned_text]).values)

    # 4) Concatenate both feature vectors
    combined_features = hstack([tfidf_features, pattern_features], format="csr")

    # 5) Run prediction with XGBoost model
    ml_probability = model.predict_proba(combined_features)[0][1]

    # --- Scam flags ---
    # CRITICAL FIX: Use cleaned_text instead of original text
    flags = detect_scam_flags(cleaned_text)  # ← CHANGED FROM: detect_scam_flags(text)

    # --- Risk scoring ---
    risk = compute_risk_score(ml_probability, flags)

    # --- Explanation ---
    explanation = generate_explanation(flags, risk["risk_level"])

    # 6) Return requested outputs and retain legacy keys for compatibility.
    return {
        "ml_probability": float(ml_probability),
        "detected_scam_features": detected_scam_features,
        "final_risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "flags": flags,
        "explanation": explanation
    }