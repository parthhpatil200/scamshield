"""
Generate synthetic legitimate SMS messages for training data augmentation.

Focus:
- Upscale legitimate volume.
- Add hard-negative contexts that contain risky keywords (OTP, urgent, verify,
  payment, toll, delivery, refund, subscription, gift card, crypto) but are
  clearly authentic/safe.
"""

import argparse
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

# Hard-negative templates: legitimate content with scam-like keywords.
SECURITY_ADVISORY_TEMPLATES = [
    "Security Alert: Never share OTP, PIN, CVV, or passwords with anyone. Bank staff will never ask.",
    "Important: If you receive urgent payment or toll messages from unknown numbers, do not click links.",
    "Fraud Advisory: Ignore texts asking to verify account via unknown links. Use only official banking app.",
    "Customer Notice: We never request OTP/UPI PIN over calls, SMS, or WhatsApp.",
    "Cyber Safety: Do not share card details, CVV, netbanking password, or verification code with anyone.",
    "Security Update: Genuine bank messages include anti-fraud warning 'Do not share OTP'.",
    "Awareness Alert: Gift card code requests claiming to be your boss are fraudulent. Report immediately.",
    "Public Notice: Tax, utility, and toll scams may create urgency. Verify using official websites only.",
]

DELIVERY_UPDATE_TEMPLATES = [
    "Order Update: Your package {pkg} from {merchant} is out for delivery today. No payment required.",
    "Delivery Confirmation: Parcel {pkg} delivered successfully at {time}. Thank you for shopping with {merchant}.",
    "Logistics Update: Shipment {pkg} has reached local hub and will be delivered by {date}.",
    "Delivery Notice: Your package {pkg} is delayed due to weather. Revised ETA: {date}. No action needed.",
    "Courier Alert: Address verification completed for shipment {pkg}. Delivery is scheduled for {date}.",
    "Package Status: Item {pkg} has been shipped and is in transit. Track in official app.",
]

TOLL_RECEIPT_TEMPLATES = [
    "FASTag Receipt: Toll Rs {amount} deducted for vehicle {vehicle}. Balance: Rs {balance}.",
    "E-ZPass Receipt: Toll charge ${usd} processed successfully. Ref: {txn_id}.",
    "SunPass Update: Toll payment of ${usd} completed. No dues pending.",
    "NHAI FASTag: Toll transaction successful for vehicle {vehicle}. Deducted Rs {amount}.",
    "Toll Statement: Monthly summary generated. View details in official app. No immediate payment required.",
]

SUBSCRIPTION_INVOICE_TEMPLATES = [
    "Invoice: Your {service} subscription renewed for Rs {amount}. Ref: {txn_id}.",
    "Payment Success: {service} monthly plan of Rs {amount} has been processed.",
    "Billing Update: {service} renewal due on {date}. Manage auto-pay in official app.",
    "Subscription Notice: Your {service} plan will renew on {date}. No action required if unchanged.",
    "Reminder: Upcoming renewal for {service}. Please review your plan settings in account dashboard.",
]

REFUND_PROCESSED_TEMPLATES = [
    "Refund Processed: Rs {amount} for order {order_id} has been credited to your original payment method.",
    "Refund Update: Your refund of Rs {amount} is initiated and will reflect within 3-5 working days.",
    "Transaction Reversal: Rs {amount} has been reversed to account {account}. Ref: {txn_id}.",
    "Merchant Refund: Rs {amount} credited successfully. No further action required.",
    "Payment Reversal Complete: Rs {amount} for failed transaction has been auto-refunded.",
]

ACCOUNT_VERIFICATION_SAFE_TEMPLATES = [
    "Account Notice: KYC remains valid. For profile updates, use official app only. Do not share OTP.",
    "Verification Reminder: Review account details in official app before {date}. No phone verification needed.",
    "Security Check Complete: Your account verification is successful. No further action is required.",
    "Profile Alert: If you did not request account changes, contact official support immediately.",
    "Customer Update: PAN/Aadhaar linking status is up to date. Avoid third-party links for verification.",
]

JOB_RECRUITER_AWARENESS_TEMPLATES = [
    "Fraud Alert: Legitimate employers never ask task fees, wallet top-ups, or advance payment for jobs.",
    "Safety Tip: Ignore 'easy remote task' messages promising daily income with upfront deposits.",
    "Cyber Cell Advisory: Report fake recruiter and task scams asking you to buy credits to withdraw earnings.",
]

CRYPTO_AWARENESS_TEMPLATES = [
    "Investment Advisory: Guaranteed crypto returns are high-risk claims. Verify platforms before investing.",
    "Security Notice: Do not share wallet seed phrases, OTPs, or exchange passwords with anyone.",
    "Bank Alert: We do not provide crypto trading tips over SMS. Beware of pump-and-dump messages.",
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


def random_vehicle():
    """Generate a random vehicle number string"""
    state = random.choice(["KA", "MH", "DL", "TN", "GJ", "UP", "TS", "RJ"])
    return f"{state}{random.randint(10,99)}{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1000,9999)}"


def random_time():
    """Generate random HH:MM time"""
    return f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"


def random_service():
    """Generate common subscription services"""
    return random.choice([
        "Netflix", "Amazon Prime", "Spotify", "Hotstar", "YouTube Premium",
        "Apple iCloud", "Microsoft 365", "Adobe CC", "JioCinema"
    ])


def random_order_id():
    """Generate a random order id"""
    return f"ORD{random.randint(100000, 999999)}"


def random_pkg_id():
    """Generate a random package/shipment id"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choices(chars, k=10))


def generate_messages(num_samples=30000):
    """Generate legitimate SMS messages with hard-negative contexts."""
    
    messages = []
    
    # Distribution keeps core banking messages while adding contextual hard negatives.
    num_debit = int(num_samples * 0.18)
    num_credit = int(num_samples * 0.14)
    num_otp = int(num_samples * 0.18)
    num_balance = int(num_samples * 0.08)
    num_payment = int(num_samples * 0.10)
    num_txn = int(num_samples * 0.07)
    num_security = int(num_samples * 0.08)
    num_delivery = int(num_samples * 0.05)
    num_toll = int(num_samples * 0.04)
    num_subscription = int(num_samples * 0.03)
    num_refund = int(num_samples * 0.03)
    num_verification_safe = int(num_samples * 0.01)
    num_job_awareness = int(num_samples * 0.005)
    num_crypto_awareness = num_samples - (
        num_debit + num_credit + num_otp + num_balance + num_payment + num_txn
        + num_security + num_delivery + num_toll + num_subscription + num_refund
        + num_verification_safe + num_job_awareness
    )
    
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

    # Generate security advisories with risky keywords in safe context.
    for _ in range(num_security):
        messages.append(random.choice(SECURITY_ADVISORY_TEMPLATES))

    # Generate legitimate delivery updates.
    for _ in range(num_delivery):
        template = random.choice(DELIVERY_UPDATE_TEMPLATES)
        messages.append(template.format(
            pkg=random_pkg_id(),
            merchant=random_merchant(),
            time=random_time(),
            date=random_date(),
        ))

    # Generate legitimate toll receipts.
    for _ in range(num_toll):
        template = random.choice(TOLL_RECEIPT_TEMPLATES)
        messages.append(template.format(
            amount=random_amount(),
            usd=round(random.uniform(1.0, 20.0), 2),
            vehicle=random_vehicle(),
            balance=random_balance(),
            txn_id=random_txn_id(),
        ))

    # Generate legitimate subscription invoices and reminders.
    for _ in range(num_subscription):
        template = random.choice(SUBSCRIPTION_INVOICE_TEMPLATES)
        messages.append(template.format(
            service=random_service(),
            amount=random_amount(),
            date=random_date(),
            txn_id=random_txn_id(),
        ))

    # Generate legitimate refunds.
    for _ in range(num_refund):
        template = random.choice(REFUND_PROCESSED_TEMPLATES)
        messages.append(template.format(
            amount=random_amount(),
            order_id=random_order_id(),
            account=random_account(),
            txn_id=random_txn_id(),
        ))

    # Generate safe verification/account notices.
    for _ in range(num_verification_safe):
        template = random.choice(ACCOUNT_VERIFICATION_SAFE_TEMPLATES)
        messages.append(template.format(date=random_date()))

    # Generate anti-scam awareness SMS (still legitimate).
    for _ in range(num_job_awareness):
        messages.append(random.choice(JOB_RECRUITER_AWARENESS_TEMPLATES))

    for _ in range(num_crypto_awareness):
        messages.append(random.choice(CRYPTO_AWARENESS_TEMPLATES))
    
    # Shuffle messages
    random.shuffle(messages)
    
    return messages


def main():
    """Generate and save legitimate banking data"""
    parser = argparse.ArgumentParser(description="Generate legitimate SMS training data.")
    parser.add_argument("--samples", type=int, default=30000, help="Number of legitimate messages to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Generating {args.samples:,} legitimate SMS messages...")
    print("=" * 60)
    
    # Generate messages
    messages = generate_messages(args.samples)
    
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
    print(f"  - Core banking txns (debit/credit/payment/txn): ~49%")
    print(f"  - OTP and verification-safe messages: ~19%")
    print(f"  - Security advisories with risky keywords: ~8%")
    print(f"  - Delivery/toll/subscription/refund legit contexts: ~15%")
    print(f"  - Fraud-awareness (job/crypto): ~1%")


if __name__ == "__main__":
    main()
