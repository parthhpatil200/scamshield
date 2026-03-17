import re
from .preprocessing import normalize_obfuscation

# --- Keyword patterns for different scam tactics ---

# --- OTP REQUEST (DANGEROUS) ---
# FIXED: Bidirectional patterns that match both "share otp" AND "otp share"
OTP_REQUEST_PATTERNS = [
    r"(?:send|share|provide|enter|tell|confirm|give|disclose).{0,30}otp",
    r"otp.{0,30}(?:send|share|provide|enter|tell|confirm|give|disclose)",
    r"\brequired.{0,20}otp",
    r"otp.{0,20}(?:required|needed|necessary)",
]

# --- OTP NOTIFICATION (SAFE) ---
OTP_NOTIFICATION_PATTERNS = [
    r"your\s+otp\s+is",
    r"your\s+verification\s+code\s+is",
    r"do\s+not\s+share",
    r"do\s+not\s+disclose",
    r"one\s+time\s+password\s+is"
]

# --- SENSITIVE FINANCIAL DATA REQUEST (EXTREMELY DANGEROUS) ---
SENSITIVE_INFO_PATTERNS = [
    r"card\s*(?:number|details|info|data)",
    r"credit\s*card",
    r"debit\s*card",
    r"confirm.*?card",
    r"verify.*?card",
    r"provide.*?card",
    r"cvv",
    r"cvc",
    r"password",
    r"pin\s*(?:code|number)?",
    r"account\s*(?:number|details)",
    r"bank\s*(?:account|details)",
    r"routing\s*number",
    r"swift\s*code",
    r"iban",
    r"ifsc",
    r"aadhaar",
    r"pan\s*(?:card|number)?",
    r"passport",
    r"ssn|social\s*security",
    r"confirm.*?(?:details|information)",
    r"verify.*?(?:account|card|payment|details)",
    r"confirm.*?info(?:rmation)?",
    r"bank.*?(?:confirm|verify)"
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
    r"\btoday\b",
    r"\bnow\b"  # Added simple "now"
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
    r"security\s*team",
    r"cyber\s*cell",
    r"officer",
    r"legal\s*department",
    r"law\s*enforcement",
    r"your\s+account",
    r"account\s+(?:status|verification|confirmation)",
    r"dear\s+(?:customer|user|member)"
]

FEAR_PATTERNS = [
    r"account.*(?:block|suspens|lock|deactivat|clos|frozen)",
    r"prevent.*(?:block|suspens|lock|deactivat|clos)",
    r"(?:will|may|be)\s+(?:block|suspens|lock|deactivat|frozen)",
    r"legal\s*action",
    r"arrest",
    r"blacklist",
    r"frozen",
    r"will\s*result\s*in",
    r"failure\s*to",
    r"unusual\s*login",
    r"permanent\s*lock",
    r"action\s+required",
    r"immediately.*(?:active|verify|confirm|restore)",
    r"(?:suspended|suspend)",  # Added
    r"service\s*(?:suspended|blocked|stopped)",  # Added
]

FINANCIAL_PATTERNS = [
    # Payment request patterns (active requests for money)
    r"transfer\s+money",
    r"send\s+money",
    r"pay\s+now",
    r"pay\s+(?:immediately|today|here)",
    r"payment\s+(?:required|due|pending)",
    r"payment\s+reminder",
    r"bank\s+transfer",
    r"account\s+transfer",
    r"account\s+payment",
    r"deposit\s+(?:amount|funds|money)",
    r"withdraw\s+(?:fee|charge)",
    r"processing\s+(?:fee|charge)",
    r"claim.*(?:prize|reward|money).*(?:pay|transfer|fee)",
    r"(?:won|win).*(?:prize|money|lakh|lottery).*(?:pay|fee)",
    r"(?:prize|lottery|reward).*(?:pay|transfer|processing|fee)",
    r"advance\s+(?:fee|payment)",
    r"claim\s+(?:reward|prize)",
    r"(?:donate|contribution).*(?:required|needed)",
    r"urgent.*(?:pay|transfer|remit)",
    r"verify.*(?:payment|transaction).*(?:complete|confirm|verify)",
]

# --- PRIZE/LOTTERY SCAM PATTERNS (for combo detection) ---
PRIZE_SCAM_PATTERNS = [
    r"congratulations.*(?:won|win)",
    r"(?:won|win).*(?:prize|lottery|lakh|crore|reward)",
    r"selected.*winner",
    r"claim.*prize",
    r"lucky.*winner",
]


# --- Helper function ---

def detect_otp_intent(text: str) -> bool:
    """
    Returns True ONLY if the message is asking the user to share/provide OTP (dangerous).
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


def detect_safe_otp_notification(text: str) -> bool:
    """
    Returns True if the message is a legitimate OTP notification with safety warnings.
    Examples: "Your OTP is XXX. Do not share it with anyone."
    """
    text = text.lower()
    
    # Check if it contains legitimate OTP notification patterns
    has_otp_notification = _match_any(OTP_NOTIFICATION_PATTERNS, text)
    
    # Additionally check for anti-scam language
    has_security_warning = _match_any([
        r"do\s+not\s+share",
        r"never\s+share",
        r"do\s+not\s+disclose",
        r"keep\s+it\s+secret",
        r"do\s+not\s+give"
    ], text)
    
    # It's a safe notification if it mentions OTP and has security warnings
    return has_otp_notification and has_security_warning


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

    # Normalize obfuscation first, then lowercase
    text = normalize_obfuscation(text)

    flags = {
        "otp_request": detect_otp_intent(text),
        "otp_notification_safe": detect_safe_otp_notification(text),
        "urgency": _match_any(URGENCY_PATTERNS, text),
        "authority_impersonation": _match_any(AUTHORITY_PATTERNS, text),
        "fear_threat": _match_any(FEAR_PATTERNS, text),
        "financial_pressure": _match_any(FINANCIAL_PATTERNS, text),
        "sensitive_info_request": _match_any(SENSITIVE_INFO_PATTERNS, text),
        "prize_scam": _match_any(PRIZE_SCAM_PATTERNS, text),
    }

    return flags