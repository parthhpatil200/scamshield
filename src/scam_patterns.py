"""Regex-based scam tactic feature extraction for ScamShield."""

import re

import pandas as pd


# OTP sharing requests (attempts to steal one-time passwords).
OTP_REQUEST_PATTERNS = [
    r"\b(?:share|send|provide|give|tell|enter|confirm|submit|disclose)\b.{0,30}\b(?:otp|one\s*time\s*password|verification\s*code|security\s*code)\b",
    r"\b(?:otp|one\s*time\s*password|verification\s*code|security\s*code)\b.{0,30}\b(?:share|send|provide|give|tell|enter|confirm|submit|disclose)\b",
    r"\b(?:otp|verification\s*code)\b.{0,20}\b(?:required|needed|necessary)\b",  # NEW
    r"\b(?:required|needed)\b.{0,20}\b(?:otp|verification\s*code)\b",  # NEW
]

# Requests for money, payment, transfer, card/bank details, or fee collection.
FINANCIAL_REQUEST_PATTERNS = [
    r"\b(?:pay|payment|transfer|send\s*money|deposit|remit|wire)\b",
    r"\b(?:processing\s*fee|service\s*fee|advance\s*fee|charges?)\b",
    r"\b(?:card\s*(?:number|details)?|cvv|cvc|upi\s*pin|pin\s*code|bank\s*details?|account\s*details?)\b",
]

# Pressure tactics that force immediate action.
URGENCY_LANGUAGE_PATTERNS = [
    r"\b(?:urgent|immediately|act\s*now|right\s*now|asap|final\s*warning|last\s*chance)\b",
    r"\b(?:within\s*\d+\s*(?:minutes?|hours?|days?)|today\s*only|expires?\s*(?:today|soon))\b",
]

# Claims of being trusted institutions or officials.
AUTHORITY_IMPERSONATION_PATTERNS = [
    r"\b(?:bank|rbi|government|income\s*tax|police|cyber\s*cell|legal\s*department|customer\s*care|support\s*team|official)\b",
    r"\b(?:dear\s*(?:customer|user|member)|account\s*(?:verification|suspension|blocked|locked))\b",
]

# Fake rewards, lottery wins, or prize claims.
REWARD_PROMISE_PATTERNS = [
    r"\b(?:congratulations|you\s*won|winner|lucky\s*draw|lottery|prize|reward|cashback|gift)\b",
    r"\b(?:claim\s*(?:your\s*)?(?:prize|reward|gift)|selected\s*as\s*winner)\b",
]

# Presence of URLs that often appear in phishing/smishing messages.
LINK_PRESENT_PATTERNS = [
    r"https?://\S+",
    r"\bwww\.\S+",
    r"\b\S+\.(?:com|in|org|net|co|io|ru|xyz)(?:/\S*)?\b",
]

# Requests to call/share a phone number or messages containing callback numbers.
PHONE_NUMBER_REQUEST_PATTERNS = [
    r"\b(?:call|contact|whatsapp|sms|text)\b.{0,20}\b(?:us|me|now|immediately|support|helpline|team)\b",
    r"\b(?:share|provide|send|confirm)\b.{0,20}\b(?:phone\s*number|mobile\s*number|contact\s*number)\b",
    r"\b(?:call|contact|whatsapp)\b.{0,20}(?:\+?\d[\d\s\-]{7,}\d)",
    r"(?:\+?\d[\d\s\-]{9,}\d)",
]

# Fake delivery / shipping fee scams (USPS, FedEx, DHL, customs).
DELIVERY_SCAM_PATTERNS = [
    r"\b(?:usps|fedex|dhl|ups|courier|parcel|shipment|delivery)\b.{0,50}\b(?:fee|pay|customs?|release|hold|pending)\b",
    r"\b(?:package|parcel|shipment)\b.{0,40}\b(?:held|detained|suspended|unpaid|failed|pending)\b",
    r"\b(?:pay|settle|clear)\b.{0,30}\b(?:customs?|shipping|handling|redelivery|import)\s*(?:fee|charge|duty)\b",
    r"\bdelivery\s*(?:failed|pending|suspended|problem|issue)\b",
]

# Toll / government fee scams.
TOLL_SCAM_PATTERNS = [
    r"\b(?:e-?zpass|sunpass|fastag|nhai|toll)\b.{0,50}\b(?:unpaid|overdue|due|outstanding|pay|fine|penalty)\b",
    r"\bunpaid\s*toll\b",
    r"\btoll\s*(?:violation|fee|balance|charge|fine)\b",
]

# Gift-card demand scams (boss impersonation, forced gift-card purchase).
GIFT_CARD_SCAM_PATTERNS = [
    r"\b(?:buy|purchase|get)\b.{0,40}\b(?:gift\s*cards?|amazon\s*cards?|google\s*play|itunes|steam)\b",
    r"\bgift\s*card\b.{0,40}\b(?:codes?|redemption|send|text|share)\b",
    r"\b(?:amazon|google|apple|itunes|steam|walmart)\b.{0,20}\bgift\s*cards?\b",
]


def _has_pattern(text: str, patterns: list[str]) -> int:
    """Return 1 if any regex pattern matches the input text, else 0."""
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return 1
    return 0


def extract_scam_features(text: str) -> dict[str, int]:
    """Extract binary scam-tactic features from a single message.

    Args:
        text: Input SMS or chat message.

    Returns:
        Dictionary with 0/1 feature values for each scam pattern category.
    """
    safe_text = text if isinstance(text, str) else ""

    return {
        "otp_request": _has_pattern(safe_text, OTP_REQUEST_PATTERNS),
        "financial_request": _has_pattern(safe_text, FINANCIAL_REQUEST_PATTERNS),
        "urgency_language": _has_pattern(safe_text, URGENCY_LANGUAGE_PATTERNS),
        "authority_impersonation": _has_pattern(safe_text, AUTHORITY_IMPERSONATION_PATTERNS),
        "reward_promise": _has_pattern(safe_text, REWARD_PROMISE_PATTERNS),
        "link_present": _has_pattern(safe_text, LINK_PRESENT_PATTERNS),
        "phone_number_request": _has_pattern(safe_text, PHONE_NUMBER_REQUEST_PATTERNS),
        "delivery_scam": _has_pattern(safe_text, DELIVERY_SCAM_PATTERNS),
        "toll_scam": _has_pattern(safe_text, TOLL_SCAM_PATTERNS),
        "gift_card_scam": _has_pattern(safe_text, GIFT_CARD_SCAM_PATTERNS),
    }


def extract_features_batch(texts: list[str]) -> pd.DataFrame:
    """Convert a list of texts into a scam-pattern feature DataFrame.

    Args:
        texts: List of SMS/chat messages.

    Returns:
        pandas DataFrame where each row corresponds to one text and each
        column is a binary scam pattern feature.
    """
    rows = [extract_scam_features(text) for text in texts]
    return pd.DataFrame(rows, columns=[
        "otp_request",
        "financial_request",
        "urgency_language",
        "authority_impersonation",
        "reward_promise",
        "link_present",
        "phone_number_request",
        "delivery_scam",
        "toll_scam",
        "gift_card_scam",
    ])
