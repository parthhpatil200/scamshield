from joblib import load
from .preprocessing import clean_text
from .flags import detect_scam_flags
from .risk_engine import compute_risk_score
from .explanation import generate_explanation

# Load trained artifacts once
MODEL_PATH = r"D:\scamshield\models\scam_classifier.pkl"
VECTORIZER_PATH = r"D:\scamshield\models\vectorizer.pkl"

model = load(MODEL_PATH)
vectorizer = load(VECTORIZER_PATH)


def analyze_text(text: str) -> dict:
    """
    Full ScamShield inference pipeline.
    """

    # --- ML probability ---
    cleaned_text = clean_text(text)
    vectorized_text = vectorizer.transform([cleaned_text])
    ml_probability = model.predict_proba(vectorized_text)[0][1]

    # --- Scam flags ---
    flags = detect_scam_flags(text)

    # --- Risk scoring ---
    risk = compute_risk_score(ml_probability, flags)

    # --- Explanation ---
    explanation = generate_explanation(flags, risk["risk_level"])

    return {
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "flags": flags,
        "explanation": explanation
    }
