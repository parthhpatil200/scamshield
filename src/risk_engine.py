ML_WEIGHT = 0.85  # ML-dominant scoring
PATTERN_WEIGHT = 0.15  # Rules provide a light adjustment

PATTERN_WEIGHTS = {
    "otp_request": 15,
    "urgency": 10,
    "authority_impersonation": 10,
    "fear_threat": 10,
    "financial_pressure": 10,
    "sensitive_info_request": 20,
    "prize_scam": 5,
}
PATTERN_MAX_SCORE = sum(PATTERN_WEIGHTS.values())


def compute_risk_score(ml_probability: float, flags: dict) -> dict:
    """
    Computes final scam risk score and level.
    ml_probability: float between 0 and 1
    flags: dictionary of detected scam flags
    """

    # --- ML score ---
    ml_prob = max(0.0, min(float(ml_probability), 1.0))
    ml_score = ml_prob * 100

    # --- Pattern score based on detected scam features (normalized 0-100) ---
    raw_pattern_score = 0
    for feature_name, weight in PATTERN_WEIGHTS.items():
        if flags.get(feature_name):
            raw_pattern_score += weight

    pattern_score = (raw_pattern_score / PATTERN_MAX_SCORE) * 100 if PATTERN_MAX_SCORE else 0

    # Safe OTP notification should only slightly reduce rule influence, not override ML.
    if flags.get("otp_notification_safe") and raw_pattern_score == 0:
        pattern_score = 0

    # --- ML-dominant weighted blend ---
    blended_score = (ml_score * ML_WEIGHT) + (pattern_score * PATTERN_WEIGHT)

    # --- Cap score ---
    final_score = min(max(int(round(blended_score)), 0), 100)

    # --- Risk level ---
    if final_score <= 30:
        risk_level = "Low"
    elif final_score <= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "risk_score": final_score,
        "risk_level": risk_level
    }
