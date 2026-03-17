from src.pipeline import analyze_text
import json

test_cases = [
    ("Legitimate OTP", "Your OTP for login is 482193. Do not share it with anyone."),
    ("Dangerous OTP", "Share your OTP immediately to secure your account."),
    ("Account Threat", "Dear customer, your account will be blocked. Share OTP immediately to restore access."),
    ("Prize Scam", "Congratulations! You won 10 lakh rupees. Pay processing fee to claim prize."),
    ("Obfuscated OTP+Fear", "Sh@re y0ur O.T.P t0 prevent acc0unt suspensi0n."),
    ("Bank Card Scam", "Hi sir, bank team here helping you. Please confirm card number for verification."),
    ("Transaction Notification", "Rs 2000 debited from account ending 1234.")
]

for name, text in test_cases:
    result = analyze_text(text)
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Risk Score: {result['risk_score']} | Risk Level: {result['risk_level']}")
    print(f"Flags: {json.dumps(result['flags'], indent=2)}")
    print(f"Explanation: {result['explanation']}")
