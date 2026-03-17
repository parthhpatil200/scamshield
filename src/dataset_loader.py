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

def load_legitimate_banking(data_path: str) -> pd.DataFrame:
    """
    Load legitimate banking messages and force them to ham (label=0).
    """
    try:
        df = pd.read_csv(data_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except UnicodeDecodeError:
            df = pd.read_csv(data_path, encoding='latin-1')
    except FileNotFoundError:
        print(f"  WARNING: Legitimate banking dataset not found at {data_path}")
        print("  Training will proceed without legitimate banking samples")
        return pd.DataFrame(columns=['text', 'label'])

    # Support either `text` or `message` column naming.
    if 'text' not in df.columns and 'message' in df.columns:
        df = df.rename(columns={'message': 'text'})

    if 'text' not in df.columns:
        print(f"  WARNING: Legitimate banking dataset missing text column. Found: {list(df.columns)}")
        return pd.DataFrame(columns=['text', 'label'])

    # Per requirement: legitimate banking messages are non-spam.
    df['label'] = 0
    df = df[['text', 'label']]
    df = df.dropna(subset=['text'])
    df = df[df['text'].str.strip().str.len() > 0]

    return df


def load_dataset_5971(data_path: str) -> pd.DataFrame:
    """Load Dataset_5971.csv and normalize to text/label format.

    Expected columns:
    - LABEL: ham/spam/smishing
    - TEXT: message body
    """
    try:
        df = pd.read_csv(data_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except UnicodeDecodeError:
            df = pd.read_csv(data_path, encoding='latin-1')
    except FileNotFoundError:
        print(f"  WARNING: Dataset_5971.csv not found at {data_path}")
        return pd.DataFrame(columns=['text', 'label'])

    # Normalize column names for downstream compatibility.
    rename_map = {
        'LABEL': 'label',
        'TEXT': 'text',
    }
    df = df.rename(columns=rename_map)

    if 'text' not in df.columns or 'label' not in df.columns:
        print(f"  WARNING: Dataset_5971.csv missing required columns. Found: {list(df.columns)}")
        return pd.DataFrame(columns=['text', 'label'])

    # Normalize labels: ham=0, spam/smishing=1
    df['label'] = df['label'].astype(str).str.strip().str.lower().map({
        'ham': 0,
        'spam': 1,
        'smishing': 1,
    })

    df = df[['text', 'label']]
    df = df.dropna(subset=['text', 'label'])
    df['label'] = df['label'].astype(int)
    df = df[df['text'].astype(str).str.strip().str.len() > 0]

    return df


def balance_binary_labels(
    df: pd.DataFrame,
    target_spam_ratio: float = 0.40,
    random_state: int = 42,
) -> pd.DataFrame:
    """Balance binary labels by downsampling the majority class.

    Strategy:
    - Keep all minority class rows.
    - Downsample majority class to approach target_spam_ratio.
    """
    if df.empty or "label" not in df.columns:
        return df

    if target_spam_ratio <= 0 or target_spam_ratio >= 1:
        raise ValueError("target_spam_ratio must be between 0 and 1")

    ham_df = df[df["label"] == 0]
    spam_df = df[df["label"] == 1]

    ham_count = len(ham_df)
    spam_count = len(spam_df)

    if ham_count == 0 or spam_count == 0:
        return df

    current_spam_ratio = spam_count / (ham_count + spam_count)

    # Already close enough to target: skip reshaping.
    if abs(current_spam_ratio - target_spam_ratio) <= 0.01:
        return df

    # Determine desired class counts while preserving minority samples.
    if current_spam_ratio < target_spam_ratio:
        # Spam is minority: keep spam, downsample ham.
        target_ham = int(round(spam_count * (1 - target_spam_ratio) / target_spam_ratio))
        if target_ham >= ham_count:
            return df
        ham_sampled = ham_df.sample(n=target_ham, random_state=random_state)
        balanced_df = pd.concat([spam_df, ham_sampled], ignore_index=True)
    else:
        # Ham is minority: keep ham, downsample spam.
        target_spam = int(round(ham_count * target_spam_ratio / (1 - target_spam_ratio)))
        if target_spam >= spam_count:
            return df
        spam_sampled = spam_df.sample(n=target_spam, random_state=random_state)
        balanced_df = pd.concat([ham_df, spam_sampled], ignore_index=True)

    balanced_df = balanced_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return balanced_df


def merge_and_dedupe_datasets(
    data_dir: str = None,
    target_spam_ratio: float = 0.40,
    balance_labels: bool = True,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Load and merge all datasets with deduplication.
    
    Merges:
    1. spam.csv (original labeled dataset - RELIABLE)
    2. Combined-Labeled-Dataset.csv (only smishing labels - PARTIALLY RELIABLE)
    3. synthetic_scams.csv (generated OTP/financial scams - ESSENTIAL)
    4. synthetic_scams_2026.csv (2026 threat patterns: delivery, toll, gift-card, crypto, etc.)
    5. legitimate_banking_samples.csv (legitimate banking notifications, forced to label=0)
    6. Dataset_5971.csv (ham/spam/smishing labels)
    
    Args:
        data_dir: Path to data directory. If None, uses project structure.
    
    Returns:
        Combined DataFrame with columns: text, label.
        If balance_labels=True, applies downsampling to approach target_spam_ratio.
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    else:
        data_dir = Path(data_dir)

    spam_path = data_dir / "spam.csv"
    combined_path = data_dir / "Combined-Labeled-Dataset.csv"
    synthetic_path = data_dir / "synthetic_scams.csv"
    synthetic_2026_path = data_dir / "synthetic_scams_2026.csv"
    banking_path = data_dir / "legitimate_banking_samples.csv"
    dataset_5971_path = data_dir / "Dataset_5971.csv"

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

    # Load 2026 threat pattern scams (delivery, toll, gift-card, crypto, etc.)
    print("\n📂 Loading synthetic_scams_2026.csv...")
    df_synthetic_2026 = load_synthetic_scams(str(synthetic_2026_path))
    if len(df_synthetic_2026) > 0:
        print(f"  ✅ Loaded {len(df_synthetic_2026)} 2026 scam pattern messages")
    else:
        print(f"  ⚠️  synthetic_scams_2026.csv not found — run generate_synthetic_scams_2026.py")
    
    # Load legitimate banking samples (to improve model robustness)
    print("\n📂 Loading legitimate_banking_samples.csv...")
    df_banking = load_legitimate_banking(str(banking_path))
    print(f"  ✅ Loaded {len(df_banking)} legitimate banking samples")

    # Load Dataset_5971 (ham/spam/smishing)
    print("\n📂 Loading Dataset_5971.csv...")
    df_5971 = load_dataset_5971(str(dataset_5971_path))
    print(f"  ✅ Loaded {len(df_5971)} rows from Dataset_5971.csv")

    # Merge all datasets
    print("\n🔀 Merging datasets...")
    dataframes_to_merge = [df_spam, df_combined, df_synthetic, df_synthetic_2026, df_banking, df_5971]
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
    print(f"  Final dataset size before balancing: {len(df_deduped)}")

    # Optional class balancing to prevent overfitting toward majority class.
    if balance_labels:
        print("\n⚖️  Balancing label distribution...")
        before_balance = len(df_deduped)
        df_deduped = balance_binary_labels(
            df_deduped,
            target_spam_ratio=target_spam_ratio,
            random_state=random_state,
        )
        print(f"  Rows before balancing: {before_balance}")
        print(f"  Rows after balancing:  {len(df_deduped)}")

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