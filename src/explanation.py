def generate_explanation(flags: dict, risk_level: str) -> str:
    """
    Generates a human-readable explanation for the scam risk.
    """

    # --- Special case: Safe OTP notification ---
    if flags.get("otp_notification_safe"):
        return (
            "This appears to be a legitimate OTP notification and includes advice not to share the code, "
            "which is typical of secure authentication messages."
        )

    reasons = []

    if flags.get("sensitive_info_request"):
        reasons.append("requests sensitive financial information such as card details, PIN, or account numbers")

    if flags.get("otp_request"):
        reasons.append("requests sensitive information like an OTP")

    if flags.get("prize_scam") and flags.get("financial_pressure"):
        reasons.append("uses a prize/lottery scam tactic requiring payment (advance-fee fraud)")
    elif flags.get("financial_pressure"):
        reasons.append("pressures the user to send or transfer money")

    if flags.get("urgency"):
        reasons.append("creates urgency to pressure immediate action")

    if flags.get("authority_impersonation"):
        reasons.append("impersonates a trusted authority such as a bank or official service")

    if flags.get("fear_threat"):
        reasons.append("uses fear or threats to manipulate the recipient")

    # --- LOW RISK EXPLANATION ---
    if risk_level == "Low":
        if not reasons:
            return (
                "This message is classified as Low risk because it does not request sensitive information, "
                "create urgency, or pressure for payment. Users should still verify the sender before sharing "
                "any personal details."
            )
        else:
            return (
                "This message is classified as Low risk. Although it contains some cautionary language, "
                "it does not exhibit strong scam behaviors such as credential requests or financial pressure."
            )

    # --- MEDIUM / HIGH RISK EXPLANATION ---
    if not reasons:
        # Fallback when ML detected spam but no rules fired
        return (
            f"This message is classified as {risk_level} risk. "
            "The content exhibits characteristics typical of scam messages, "
            "including suspicious language patterns and fraudulent intent."
        )

    explanation = (
        f"This message is classified as {risk_level} risk because it "
        + ", and ".join(reasons)
        + "."
    )

    return explanation
