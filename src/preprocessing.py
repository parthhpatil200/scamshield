import re

def normalize_obfuscation(text: str) -> str:
    """
    Normalize common obfuscation patterns used to bypass filters.
    
    Examples:
    - 0 → o (y0ur → your)
    - 1 → i (v1agra → viagra)
    - 3 → e (pr0m0t3 → promote)
    - 4 → a (gr34t → great)
    - 5 → s (bank5 → banks)
    - 7 → t (7ransfer → transfer)
    - @ → a (sh@re → share)
    - $ → s ($end → send)
    - Remove dots inside words (O.T.P → OTP)
    """
    text = text.lower()
    
    # ===== NEW: Normalize OTP variations BEFORE character substitution =====
    # This handles: 0-T-P, O.T.P, 0.T.P, O-T-P → otp
    text = re.sub(r'\b[o0][\s\.\-_]*[t7][\s\.\-_]*p\b', 'otp', text, flags=re.IGNORECASE)
    
    # ===== NEW: Normalize common SMS slang =====
    slang_map = {
        r'\bur\b': 'your',    # ur → your
        r'\bu\b': 'you',      # u → you
        r'\b2\b': 'to',       # 2 → to (when standalone)
        r'\b4\b': 'for',      # 4 → for (when standalone)
    }
    for pattern, replacement in slang_map.items():
        text = re.sub(pattern, replacement, text)
    # ===== END NEW CODE =====
    
    # Character substitution mapping
    obfuscation_map = {
        '0': 'o',
        '1': 'i',
        '3': 'e',
        '4': 'a',
        '5': 's',
        '7': 't',
        '@': 'a',
        '$': 's',
        '!': 'i',
    }
    
    # Apply substitutions
    for char, replacement in obfuscation_map.items():
        text = text.replace(char, replacement)
    
    # Remove dots and underscores inside words (O.T.P, O_T_P → OTP)
    text = re.sub(r'([a-z])[._]([a-z])', r'\1\2', text)
    text = re.sub(r'([a-z])[._]([a-z])', r'\1\2', text)  # Run twice for multi-char sequences
    
    return text


def clean_text(text: str) -> str:
    """
    Clean and normalize text for ML processing.
    """
    # First normalize obfuscation
    text = normalize_obfuscation(text)
    
    # Then standard cleaning
    text = re.sub(r"[^a-z0-9\s]", " ", text)    # replace non-alphanumeric characters with space
    text = re.sub(r"\s+", " ", text).strip()     # replace multiple spaces with single space, then strip
    return text