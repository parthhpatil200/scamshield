def compute_risk_score(ml_probability: float, flags: dict) -> dict:
    """
    Computes final scam risk score and level.
    ml_probability: float between 0 and 1
    flags: dictionary of detected scam flags
    """

    # --- Base risk from ML ---
    base_score = ml_probability * 100

    # --- Flag-based penalties ---
    if flags.get("otp_request"):
        base_score += 15

    if flags.get("urgency"):
        base_score += 10

    if flags.get("authority_impersonation"):
        base_score += 10

    if flags.get("fear_threat"):
        base_score += 10

    if flags.get("financial_pressure"):
        base_score += 10

    # --- Cap score ---
    final_score = min(int(base_score), 100)

    # --- Risk level ---
    if final_score <= 30:
        risk_level = "Low"
    elif final_score <= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # --- HARD ESCALATION RULES ---
    if flags.get("authority_impersonation") and flags.get("fear_threat"):
        risk_level = "High"
        final_score = max(final_score, 70)

    return {
        "risk_score": final_score,
        "risk_level": risk_level
    }
