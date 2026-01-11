import re

# --- Keyword patterns for different scam tactics ---

# --- OTP REQUEST (DANGEROUS) ---
OTP_REQUEST_PATTERNS = [
    r"send\s+otp",
    r"share\s+otp",
    r"provide\s+otp",
    r"enter\s+otp",
    r"tell\s+us\s+the\s+otp",
    r"confirm\s+otp"
]

# --- OTP NOTIFICATION (SAFE) ---
OTP_NOTIFICATION_PATTERNS = [
    r"your\s+otp\s+is",
    r"your\s+verification\s+code\s+is",
    r"do\s+not\s+share",
    r"do\s+not\s+disclose",
    r"one\s+time\s+password\s+is"
]

URGENCY_PATTERNS = [
    r"urgent",
    r"immediately",
    r"act\s*now",
    r"within\s*\d+\s*hours?",
    r"last\s*chance",
    r"expires?\s*today",
    r"verify\s*now",
    r"immediately\s*verify",
    r"as\s*soon\s*as\s*possible",
    r"urgent\s*action\s*required",
    r"final\s*reminder",
    r"pay\s*now",
    r"pay\s*immediately",
    r"pay\s*today",
    r"\btoday\b"

]

AUTHORITY_PATTERNS = [
    r"bank",
    r"customer\s*care",
    r"support\s*team",
    r"government",
    r"income\s*tax",
    r"police",
    r"official",
    r"\brbi\b",
    r"\bkyc\b",
    r"\buidai\b",
    r"\bpan\b",
    r"\baadhaar\b",
    r"customer\s*support",
    r"support\s*team",
    r"security\s*team",
    r"cyber\s*cell",
    r"police",
    r"officer",
    r"legal\s*department",
    r"law\s*enforcement"
]

FEAR_PATTERNS = [
    r"account\s*blocked",
    r"account\s*suspended",
    r"legal\s*action",
    r"arrest",
    r"blacklisted",
    r"frozen",
    r"will\s*result\s*in",
    r"failure\s*to",
    r"account\s*suspension",
    r"unusual\s*login",
    r"permanent\s*lock",
    r"account\s*lock"
]

FINANCIAL_PATTERNS = [
    r"transfer\s*money",
    r"send\s*money",
    r"pay\s*now",
    r"payment\s*required",
    r"debit",
    r"credit",
    r"bank\s*transfer",
    r"account\s*transfer",
    r"account\s*payment",
    r"payment\s*due",
    r"payment\s*reminder",
    r"payment.*deducted"

]


# --- Helper function ---

def detect_otp_intent(text: str) -> bool:
    """
    Returns True ONLY if the message is asking the user to share/provide OTP.
    Legitimate OTP notifications are explicitly excluded.
    """
    text = text.lower()

    # If it's a notification, suppress OTP request
    for pattern in OTP_NOTIFICATION_PATTERNS:
        if re.search(pattern, text):
            return False

    # Otherwise, check if it is asking for OTP
    for pattern in OTP_REQUEST_PATTERNS:
        if re.search(pattern, text):
            return True

    return False

def _match_any(patterns, text):
    """
    Returns True if any regex pattern matches the text.
    """
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False


# --- Main flag detection function ---

def detect_scam_flags(text: str) -> dict:
    """
    Detects scam-related behavioral flags in the given text.
    """

    text = text.lower()

    flags = {
        "otp_request": detect_otp_intent(text),
        "urgency": _match_any(URGENCY_PATTERNS, text),
        "authority_impersonation": _match_any(AUTHORITY_PATTERNS, text),
        "fear_threat": _match_any(FEAR_PATTERNS, text),
        "financial_pressure": _match_any(FINANCIAL_PATTERNS, text),
    }

    return flags
