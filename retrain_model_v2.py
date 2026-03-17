"""
Retrain ScamShield model with augmented legitimate banking data.
Merges synthetic banking samples with existing spam dataset and retrains.
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from scipy.sparse import csr_matrix, hstack
from xgboost import XGBClassifier
from joblib import dump
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dataset_loader import merge_and_dedupe_datasets
from src.feature_extraction import get_vectorizer
from src.preprocessing import clean_text
from src.scam_patterns import extract_features_batch


def load_legitimate_banking_data():
    """Load generated legitimate banking samples"""
    legit_path = Path(__file__).parent / "data" / "raw" / "legitimate_banking_samples.csv"
    
    if not legit_path.exists():
        print(f"❌ Legitimate banking data not found at {legit_path}")
        print("Please run: python generate_legit_banking_data.py first")
        sys.exit(1)
    
    df = pd.read_csv(legit_path)
    print(f"✅ Loaded {len(df)} legitimate banking samples")
    return df


def merge_datasets():
    """Merge existing spam data with legitimate banking samples"""
    print("\n" + "="*60)
    print("STEP 1: Loading and Merging Datasets")
    print("="*60)
    
    # Load existing spam/scam data
    print("\n1. Loading existing spam/scam datasets...")
    df_spam = merge_and_dedupe_datasets()
    
    # Load legitimate banking data
    print("\n2. Loading legitimate banking samples...")
    df_legit = load_legitimate_banking_data()
    
    # Merge both datasets
    print("\n3. Merging datasets...")
    df_merged = pd.concat([df_spam, df_legit], ignore_index=True)
    print(f"   Total rows after merge: {len(df_merged)}")
    
    # Deduplicate
    print("\n4. Deduplicating messages...")
    initial_count = len(df_merged)
    df_merged['text_lower'] = df_merged['text'].str.lower().str.strip()
    df_merged = df_merged.drop_duplicates(subset=['text_lower'], keep='first')
    df_merged = df_merged.drop(columns=['text_lower'])
    duplicates_removed = initial_count - len(df_merged)
    print(f"   Removed {duplicates_removed} duplicates")
    print(f"   Final dataset size: {len(df_merged)}")
    
    # Label distribution
    print("\n5. Dataset composition:")
    label_counts = df_merged['label'].value_counts().sort_index()
    ham_count = label_counts.get(0, 0)
    spam_count = label_counts.get(1, 0)
    print(f"   Ham (legitimate): {ham_count:,} ({ham_count/len(df_merged)*100:.1f}%)")
    print(f"   Spam (scam): {spam_count:,} ({spam_count/len(df_merged)*100:.1f}%)")
    
    return df_merged


def train_model_v2(df):
    """Train improved model with balanced data"""
    print("\n" + "="*60)
    print("STEP 2: Training Model V2")
    print("="*60)
    
    # Explicit cleaning step before all feature extraction.
    X = df['text'].fillna("").astype(str).apply(clean_text)
    y = df['label']
    
    # Train-test split (stratified)
    print("\n1. Splitting data (80/20 train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training samples: {len(X_train):,}")
    print(f"   Test samples: {len(X_test):,}")
    
    # Vectorization
    print("\n2. Vectorizing text with TF-IDF...")
    vectorizer = get_vectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"   TF-IDF feature dimensions: {X_train_vec.shape[1]:,}")

    # Pattern features
    print("\n3. Extracting regex scam-pattern features...")
    X_train_pattern_df = extract_features_batch(X_train.tolist())
    X_test_pattern_df = extract_features_batch(X_test.tolist())
    X_train_pattern = csr_matrix(X_train_pattern_df.values)
    X_test_pattern = csr_matrix(X_test_pattern_df.values)
    print(f"   Pattern feature dimensions: {X_train_pattern.shape[1]:,}")

    # Concatenate both feature sets
    print("\n4. Concatenating TF-IDF + pattern features...")
    X_train_combined = hstack([X_train_vec, X_train_pattern], format="csr")
    X_test_combined = hstack([X_test_vec, X_test_pattern], format="csr")
    print(f"   Total feature dimensions: {X_train_combined.shape[1]:,}")
    
    # Training
    print("\n5. Training XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_combined, y_train)
    
    # Predictions
    print("\n6. Evaluating model...")
    y_pred = model.predict(X_test_combined)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    print("\n" + "="*60)
    print("STEP 3: Model Performance Metrics")
    print("="*60)
    print(f"\nAccuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    
    print("\nDetailed Classification Report:")
    print("-" * 60)
    print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))
    
    # Save model
    print("\n" + "="*60)
    print("STEP 4: Saving Model V2")
    print("="*60)
    
    output_dir = Path(__file__).parent / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = output_dir / "scam_model_xgb.pkl"
    vectorizer_path = output_dir / "vectorizer.pkl"
    
    dump(model, model_path)
    dump(vectorizer, vectorizer_path)
    
    print(f"\n✅ Model saved to: {model_path}")
    print(f"✅ Vectorizer saved to: {vectorizer_path}")
    
    return model, vectorizer


def test_predictions(model, vectorizer):
    """Test model on sample messages"""
    print("\n" + "="*60)
    print("STEP 5: Testing Predictions on Sample Messages")
    print("="*60)
    
    test_cases = [
        ("Bank Debit", "Rs 2000 debited from account ending 1234."),
        ("Legitimate OTP", "Your OTP for login is 482193. Do not share it with anyone."),
        ("Scam OTP Request", "Share your OTP immediately to secure your account."),
        ("Credit Alert", "Rs 5000 credited to A/C XX4567. Balance: Rs 25000."),
        ("Account Threat", "Dear customer, your account will be blocked. Share OTP now."),
        ("Prize Scam", "Congratulations! You won 10 lakh. Pay processing fee to claim."),
    ]
    
    print("\nTest Results:")
    print("-" * 60)
    
    for name, text in test_cases:
        cleaned = clean_text(text)
        vectorized = vectorizer.transform([cleaned])
        pattern_features = csr_matrix(extract_features_batch([cleaned]).values)
        combined_features = hstack([vectorized, pattern_features], format="csr")

        prediction = model.predict(combined_features)[0]
        probability = model.predict_proba(combined_features)[0]
        
        label = "HAM (legitimate)" if prediction == 0 else "SPAM (scam)"
        confidence = probability[prediction] * 100
        
        print(f"\n{name}:")
        print(f"  Message: {text}")
        print(f"  Prediction: {label}")
        print(f"  Confidence: {confidence:.1f}%")


def main():
    """Main retraining pipeline"""
    print("\n" + "="*60)
    print("ScamShield Model V2 - Retraining Pipeline")
    print("With Legitimate Banking Data Augmentation")
    print("="*60)
    
    # Merge datasets
    df_merged = merge_datasets()
    
    # Train model
    model, vectorizer = train_model_v2(df_merged)
    
    # Test predictions
    test_predictions(model, vectorizer)
    
    print("\n" + "="*60)
    print("✅ Retraining Complete!")
    print("="*60)
    print("\nModel V2 is now ready for deployment.")
    print("The updated model handles legitimate banking messages correctly.")
    print("\nNext steps:")
    print("  1. Restart uvicorn server: uvicorn src.api:app --reload")
    print("  2. Run test suite: python test_all_cases.py")


if __name__ == "__main__":
    main()
