import re

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)    #replace non-alphanumeric characters with space
    text = re.sub(r"\s+", " ", text).strip()     #first replace multiple spaces with single space, then strip leading/trailing spaces
    return text
