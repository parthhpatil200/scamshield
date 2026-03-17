# This file will load data, train the model, evaluate and save the model
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from joblib import dump
from .dataset_loader import merge_and_dedupe_datasets
from .feature_extraction import get_vectorizer
from pathlib import Path

def train_model(use_merged: bool = True, data_path: str = None):
    """
    Train the scam detection model.
    
    Args:
        use_merged: If True, use merged dataset. If False, use single csv file.
        data_path: Path to single CSV if use_merged=False. If None and use_merged=True, 
                   automatically loads from data/raw.
    """
    if use_merged:
        print("Loading and merging datasets...")
        df = merge_and_dedupe_datasets(data_path)
    else:
        # Try reading as UTF-8 first; fall back to common Windows/Latin encodings if needed.
        try:
            df = pd.read_csv(data_path)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(data_path, encoding='cp1252')
                print("Warning: file decoded with 'cp1252' encoding due to UTF-8 errors.")
            except UnicodeDecodeError:
                df = pd.read_csv(data_path, encoding='latin-1')
                print("Warning: file decoded with 'latin-1' encoding due to UTF-8 errors.")

        # Support datasets that use different column names (e.g., SMS Spam Collection uses 'v1' for label and 'v2' for text).
        if 'text' not in df.columns or 'label' not in df.columns:
            if 'v2' in df.columns and 'v1' in df.columns:
                df = df.rename(columns={'v2': 'text', 'v1': 'label'})
            else:
                raise ValueError(f"Dataset must contain 'text' and 'label' columns (or 'v2'/'v1'). Found: {list(df.columns)}")

    X = df['text']    # Feature column (raw text).
    y = df['label']
    
    # Ensure labels are 0/1
    if y.dtype == 'object':
        y = y.map({'ham': 0, 'spam': 1})
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    vectorizer = get_vectorizer()   # Creates TF-IDF object with fixed configuration.
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)   # Transforms test data using the fitted vectorizer. We do not fit again to avoid data leakage.
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)
    y_pred = model.predict(X_test_vec)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Ensure repository-level `models/` directory exists and save artifacts there
    output_dir = Path(__file__).resolve().parent.parent / "models"   # No matter where this project is run from, save models in the project's models folder.
    output_dir.mkdir(parents=True, exist_ok=True)    
    dump(model, output_dir / "scam_classifier.pkl")  # Saves the trained model to a file.
    dump(vectorizer, output_dir / "vectorizer.pkl")  # Saves the vectorizer to a file.

    print(f"\nModel and vectorizer saved successfully to {output_dir}.")


if __name__ == "__main__":
    train_model(use_merged=True)
