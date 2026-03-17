"""
Generate synthetic legitimate banking SMS messages for training data augmentation.
Creates 15,000 realistic banking notifications to balance the dataset.
"""

import pandas as pd
import random
from pathlib import Path


# --- Templates for different message types ---

DEBIT_TEMPLATES = [
    "Rs {amount} debited from account {account} on {date}. Available balance: Rs {balance}.",
    "Debit Alert: Rs {amount} debited from A/C {account} at {merchant}. Avl Bal: Rs {balance}.",
    "Your account {account} has been debited by Rs {amount}. Transaction ID: {txn_id}.",
    "Rs {amount} debited from your account ending {last4} on {date}. Balance: {balance}.",
    "Debited Rs {amount} from A/C {account}. {merchant}. Ref: {txn_id}.",
    "Transaction Alert: Rs {amount} paid to {merchant}. A/C {account}. Balance: Rs {balance}.",
    "Dear Customer, Rs {amount} debited from A/C {account}. Available balance Rs {balance}.",
    "Amount of Rs {amount} debited from your account {account} at {merchant}.",
]

CREDIT_TEMPLATES = [
    "Rs {amount} credited to account {account} on {date}. Available balance: Rs {balance}.",
    "Credit Alert: Rs {amount} credited to A/C {account}. Avl Bal: Rs {balance}.",
    "Your account {account} has been credited with Rs {amount}. Transaction ID: {txn_id}.",
    "Rs {amount} credited to your account ending {last4} on {date}. Balance: {balance}.",
    "Credited Rs {amount} to A/C {account}. Ref: {txn_id}.",
    "Dear Customer, Rs {amount} credited to A/C {account}. Available balance Rs {balance}.",
    "Amount of Rs {amount} credited to your account {account}.",
    "Transaction successful: Rs {amount} received in A/C {account}.",
]

OTP_TEMPLATES = [
    "Your OTP for login is {otp}. Do not share it with anyone.",
    "Your verification code is {otp}. Valid for 10 minutes. Do not share.",
    "{otp} is your OTP for transaction. Do not disclose to anyone.",
    "Your one time password is {otp}. Never share this with anyone.",
    "OTP for login: {otp}. Keep it confidential and do not share.",
    "Your OTP is {otp}. This is valid for 5 minutes only. Do not share.",
    "Use {otp} as your verification code. Do not share this OTP.",
    "{otp} is your authentication code. Please do not share with anyone.",
    "Dear customer, your OTP is {otp}. Do not share this code with anyone.",
    "Security code: {otp}. Valid for next 10 mins. Never share your OTP.",
]

BALANCE_TEMPLATES = [
    "Your account balance as on {date} is Rs {balance}. A/C {account}.",
    "Balance enquiry: Available balance in A/C {account} is Rs {balance}.",
    "Dear Customer, your current balance is Rs {balance} for A/C {account}.",
    "A/C {account}: Balance Rs {balance} as on {date}.",
    "Account balance for {account}: Rs {balance}.",
]

PAYMENT_SUCCESS_TEMPLATES = [
    "Payment of Rs {amount} successful. Ref No: {txn_id}. Thank you.",
    "Transaction successful. Rs {amount} paid to {merchant}. Ref: {txn_id}.",
    "Your payment of Rs {amount} has been processed successfully. Txn ID: {txn_id}.",
    "Payment confirmation: Rs {amount} transferred successfully. Reference: {txn_id}.",
    "Dear customer, payment of Rs {amount} completed. Transaction ID: {txn_id}.",
]

TRANSACTION_CONFIRM_TEMPLATES = [
    "Transaction of Rs {amount} completed successfully on {date}. A/C {account}.",
    "Dear Customer, transaction successful. Amount: Rs {amount}. Ref: {txn_id}.",
    "Your transaction for Rs {amount} has been completed. ID: {txn_id}.",
    "Transaction alert: Rs {amount} transaction successful on A/C {account}.",
]

# --- Data generators ---

def random_amount():
    """Generate random transaction amounts"""
    amounts = [
        random.randint(50, 500),
        random.randint(500, 2000),
        random.randint(2000, 10000),
        random.randint(10000, 50000),
    ]
    return random.choice(amounts)


def random_account():
    """Generate random account number"""
    return f"XX{random.randint(1000, 9999)}"


def random_last4():
    """Generate last 4 digits of account"""
    return f"{random.randint(1000, 9999)}"


def random_balance():
    """Generate random account balance"""
    return random.randint(5000, 500000)


def random_otp():
    """Generate 6-digit OTP"""
    return f"{random.randint(100000, 999999)}"


def random_txn_id():
    """Generate transaction ID"""
    return f"{random.randint(100000000000, 999999999999)}"


def random_date():
    """Generate random date"""
    day = random.randint(1, 28)
    month = random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    year = random.choice(['2024', '2025', '2026'])
    return f"{day:02d}-{month}-{year}"


def random_merchant():
    """Generate random merchant/vendor name"""
    merchants = [
        "Amazon", "Flipkart", "Swiggy", "Zomato", "BookMyShow", "Uber", "Ola",
        "Big Bazaar", "DMart", "Reliance Retail", "PVR Cinemas", "IRCTC",
        "PayTM Mall", "MakeMyTrip", "Myntra", "Google Pay", "PhonePe",
        "Grocery Store", "Restaurant", "Cafe", "Supermarket", "Shopping Mall"
    ]
    return random.choice(merchants)


def generate_messages(num_samples=15000):
    """Generate legitimate banking SMS messages"""
    
    messages = []
    
    # Distribution: 30% debit, 20% credit, 30% OTP, 10% balance, 10% payment/txn
    num_debit = int(num_samples * 0.30)
    num_credit = int(num_samples * 0.20)
    num_otp = int(num_samples * 0.30)
    num_balance = int(num_samples * 0.10)
    num_payment = int(num_samples * 0.05)
    num_txn = num_samples - (num_debit + num_credit + num_otp + num_balance + num_payment)
    
    # Generate debit messages
    for _ in range(num_debit):
        template = random.choice(DEBIT_TEMPLATES)
        msg = template.format(
            amount=random_amount(),
            account=random_account(),
            last4=random_last4(),
            balance=random_balance(),
            date=random_date(),
            merchant=random_merchant(),
            txn_id=random_txn_id()
        )
        messages.append(msg)
    
    # Generate credit messages
    for _ in range(num_credit):
        template = random.choice(CREDIT_TEMPLATES)
        msg = template.format(
            amount=random_amount(),
            account=random_account(),
            last4=random_last4(),
            balance=random_balance(),
            date=random_date(),
            txn_id=random_txn_id()
        )
        messages.append(msg)
    
    # Generate OTP messages
    for _ in range(num_otp):
        template = random.choice(OTP_TEMPLATES)
        msg = template.format(otp=random_otp())
        messages.append(msg)
    
    # Generate balance enquiry messages
    for _ in range(num_balance):
        template = random.choice(BALANCE_TEMPLATES)
        msg = template.format(
            balance=random_balance(),
            account=random_account(),
            date=random_date()
        )
        messages.append(msg)
    
    # Generate payment success messages
    for _ in range(num_payment):
        template = random.choice(PAYMENT_SUCCESS_TEMPLATES)
        msg = template.format(
            amount=random_amount(),
            merchant=random_merchant(),
            txn_id=random_txn_id()
        )
        messages.append(msg)
    
    # Generate transaction confirmation messages
    for _ in range(num_txn):
        template = random.choice(TRANSACTION_CONFIRM_TEMPLATES)
        msg = template.format(
            amount=random_amount(),
            account=random_account(),
            date=random_date(),
            txn_id=random_txn_id()
        )
        messages.append(msg)
    
    # Shuffle messages
    random.shuffle(messages)
    
    return messages


def main():
    """Generate and save legitimate banking data"""
    print("Generating 15,000 legitimate banking SMS messages...")
    print("=" * 60)
    
    # Generate messages
    messages = generate_messages(15000)
    
    # Create DataFrame
    df = pd.DataFrame({
        'label': 0,  # All legitimate (ham)
        'text': messages
    })
    
    # Save to CSV
    output_path = Path(__file__).parent / "data" / "raw" / "legitimate_banking_samples.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df)} legitimate banking messages")
    print(f"✅ Saved to: {output_path}")
    print("\nSample messages:")
    print("-" * 60)
    for i, msg in enumerate(messages[:10], 1):
        print(f"{i}. {msg}")
    
    print("\nMessage type distribution:")
    print(f"  - Debit notifications: ~30%")
    print(f"  - Credit notifications: ~20%")
    print(f"  - OTP messages: ~30%")
    print(f"  - Balance enquiries: ~10%")
    print(f"  - Payment confirmations: ~10%")


if __name__ == "__main__":
    main()
