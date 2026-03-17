"""
Dataset loader and merger for multiple SMS/scam datasets.
Combines spam.csv, Combined-Labeled-Dataset.csv, and synthetic scam data
with normalization and deduplication.

UPDATED: Now includes synthetic OTP and financial scam dataset for proper training
"""

import pandas as pd
from pathlib import Path


def load_spam_dataset(data_path: str) -> pd.DataFrame:
    """
    Load the original spam.csv dataset and normalize column names.
    Maps: v1 → label (ham/spam), v2 → text
    """
    try:
        df = pd.read_csv(data_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except UnicodeDecodeError:
            df = pd.read_csv(data_path, encoding='latin-1')

    # Rename columns to standard format
    if 'v2' in df.columns and 'v1' in df.columns:
        df = df[['v1', 'v2']].rename(columns={'v1': 'label', 'v2': 'text'})
    
    # Normalize labels: ham=0, spam=1
    df['label'] = df['label'].map({'ham': 0, 'spam': 1})
    df = df.dropna(subset=['label'])
    
    return df[['text', 'label']]


def load_combined_dataset(data_path: str) -> pd.DataFrame:
    """
    Load the Combined-Labeled-Dataset.csv and normalize.
    
    CRITICAL FIX: This dataset has mislabeled data where legitimate messages
    are marked as spam=1. We now INVERT the labels since analysis showed
    most messages with spam=1 are actually legitimate notifications.
    
    Original logic: max(spam_label, smishing_label)
    Fixed logic: Only trust smishing_label, ignore spam_label
    """
    try:
        df = pd.read_csv(data_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except UnicodeDecodeError:
            df = pd.read_csv(data_path, encoding='latin-1')

    # Rename to standard format
    df = df.rename(columns={'message': 'text'})
    
    # Ensure label columns are numeric
    df['spam label'] = pd.to_numeric(df['spam label'], errors='coerce').fillna(0).astype(int)
    df['smishing label'] = pd.to_numeric(df['smishing label'], errors='coerce').fillna(0).astype(int)
    
    # CRITICAL FIX: Only use smishing_label as it's more reliable
    # The 'spam label' column has too many false positives
    # Most messages are legitimate telecom notifications mislabeled as spam
    df['label'] = df['smishing label']
    
    # Alternative: Skip Combined dataset entirely (uncomment to disable)
    # return pd.DataFrame(columns=['text', 'label'])
    
    # Keep only text and label
    df = df[['text', 'label']]
    
    # Filter out empty/null messages
    df = df.dropna(subset=['text'])
    df = df[df['text'].str.strip().str.len() > 0]
    
    return df


def load_synthetic_scams(data_path: str) -> pd.DataFrame:
    """
    Load synthetic OTP and financial scam dataset.
    
    This dataset contains 1,500 synthetic scam messages:
    - 1,000 OTP scam variations with obfuscation
    - 500 financial scam variations
    
    All messages are pre-labeled as spam (label=1)
    """
    try:
        df = pd.read_csv(data_path)
        print(f"  Loaded {len(df)} synthetic scam messages")
        
        # Ensure proper format
        if 'label' not in df.columns:
            df['label'] = 1  # All synthetic messages are scams
        
        # Keep only text and label
        df = df[['text', 'label']]
        
        # Filter out empty messages
        df = df.dropna(subset=['text'])
        df = df[df['text'].str.strip().str.len() > 0]
        
        return df
    
    except FileNotFoundError:
        print(f"  ⚠️  WARNING: Synthetic scam dataset not found at {data_path}")
        print(f"  ⚠️  Training will proceed without synthetic OTP scams")
        print(f"  ⚠️  This will result in poor OTP scam detection!")
        return pd.DataFrame(columns=['text', 'label'])


def merge_and_dedupe_datasets(data_dir: str = None) -> pd.DataFrame:
    """
    Load and merge all datasets with deduplication.
    
    Merges:
    1. spam.csv (original labeled dataset - RELIABLE)
    2. Combined-Labeled-Dataset.csv (only smishing labels - PARTIALLY RELIABLE)
    3. synthetic_scams.csv (generated OTP/financial scams - ESSENTIAL)
    
    Args:
        data_dir: Path to data directory. If None, uses project structure.
    
    Returns:
        Combined, deduplicated DataFrame with columns: text, label
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    else:
        data_dir = Path(data_dir)

    spam_path = data_dir / "spam.csv"
    combined_path = data_dir / "Combined-Labeled-Dataset.csv"
    synthetic_path = data_dir / "synthetic_scams.csv"

    # Load spam.csv (most reliable dataset)
    print("📂 Loading spam.csv...")
    df_spam = load_spam_dataset(str(spam_path))
    print(f"  ✅ Loaded {len(df_spam)} rows from spam.csv")

    # Load Combined dataset (using only smishing labels)
    print("\n📂 Loading Combined-Labeled-Dataset.csv...")
    df_combined = load_combined_dataset(str(combined_path))
    print(f"  ✅ Loaded {len(df_combined)} rows from Combined-Labeled-Dataset.csv")

    # Load synthetic scams (CRITICAL for OTP detection)
    print("\n📂 Loading synthetic_scams.csv...")
    df_synthetic = load_synthetic_scams(str(synthetic_path))
    if len(df_synthetic) > 0:
        print(f"  ✅ Loaded {len(df_synthetic)} synthetic scam messages")
    else:
        print(f"  ⚠️  No synthetic scams loaded - OTP detection will be poor!")

    # Merge all datasets
    print("\n🔀 Merging datasets...")
    dataframes_to_merge = [df_spam, df_combined, df_synthetic]
    dataframes_to_merge = [df for df in dataframes_to_merge if len(df) > 0]
    
    df_merged = pd.concat(dataframes_to_merge, ignore_index=True)
    print(f"  Total rows after merging: {len(df_merged)}")

    # Deduplicate on text (case-insensitive)
    print("\n🔄 Deduplicating messages...")
    initial_count = len(df_merged)
    df_merged['text_lower'] = df_merged['text'].str.lower().str.strip()
    df_deduped = df_merged.drop_duplicates(subset=['text_lower'], keep='first')
    df_deduped = df_deduped.drop(columns=['text_lower'])
    
    duplicates_removed = initial_count - len(df_deduped)
    print(f"  Removed {duplicates_removed} duplicates")
    print(f"  Final dataset size: {len(df_deduped)}")

    # Label distribution
    print("\n📊 Final dataset composition:")
    label_counts = df_deduped['label'].value_counts().sort_index()
    ham_count = label_counts.get(0, 0)
    spam_count = label_counts.get(1, 0)
    total = len(df_deduped)
    
    print(f"  Ham (legitimate):  {ham_count:5,} ({ham_count/total*100:5.1f}%)")
    print(f"  Spam (scam):       {spam_count:5,} ({spam_count/total*100:5.1f}%)")
    
    # Warn if dataset is heavily imbalanced
    if spam_count < ham_count * 0.2:  # Less than 20% spam
        print("\n  ⚠️  WARNING: Dataset is imbalanced (too few spam examples)")
        print(f"  ⚠️  Spam ratio: {spam_count/total*100:.1f}% (recommended: 30-50%)")
    
    # Warn if no synthetic scams were loaded
    if len(df_synthetic) == 0:
        print("\n  ⚠️  CRITICAL WARNING: No synthetic scams loaded!")
        print(f"  ⚠️  OTP scam detection will NOT work properly")
        print(f"  ⚠️  Please add synthetic_scams.csv to {data_dir}")

    return df_deduped.reset_index(drop=True)


if __name__ == "__main__":
    print("="*70)
    print("ScamShield Dataset Loader - Testing")
    print("="*70)
    print()
    
    df = merge_and_dedupe_datasets()
    
    print("\n" + "="*70)
    print("Dataset Summary")
    print("="*70)
    print(f"\nMerged dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n📝 Sample messages (5 ham, 5 spam):")
    print("\nHAM (legitimate) examples:")
    ham_samples = df[df['label'] == 0].sample(min(5, (df['label']==0).sum()), random_state=42)
    for idx, row in ham_samples.iterrows():
        print(f"  - {row['text'][:80]}")
    
    print("\nSPAM (scam) examples:")
    spam_samples = df[df['label'] == 1].sample(min(5, (df['label']==1).sum()), random_state=42)
    for idx, row in spam_samples.iterrows():
        print(f"  - {row['text'][:80]}")
    
    print("\n" + "="*70)
    print("✅ Dataset loading test complete!")
    print("="*70)