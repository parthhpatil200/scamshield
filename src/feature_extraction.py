#Core idea-> Convert text to numerical vectors with meaning

from sklearn.feature_extraction.text import TfidfVectorizer
from .preprocessing import clean_text

def get_vectorizer():
    return TfidfVectorizer(
        preprocessor=clean_text,    # Use the clean_text function from preprocessing.py
        ngram_range=(1,2),          # Use unigrams and bigrams
        max_features=5000,          # Limit to top 5000 features
        stop_words="english"        # Remove English stop words like 'the', 'is', etc.
    )