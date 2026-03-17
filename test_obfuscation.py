"""Test enhanced obfuscation normalization with extreme cases"""
from src.pipeline import analyze_text

obfuscation_tests = [
    ('Leet speak OTP', 'Sh4r3 y0ur 0.T.P 1mm3d14t3ly t0 s3cur3 4cc0unt.'),
    ('Dots + Numbers', 'C.O.N.G.R.A.T.S! Y0u w0n 1 l4kh. P4y pr0c3ss1ng f33.'),
    ('Dollar signs', '$end m0ney t0 cl41m pr1ze n0w!'),
    ('Mixed obfuscation', 'B@nk t3@m h3r3. C0nf1rm c@rd numb3r f0r v3r1f1c@t10n.'),
    ('Extreme obfuscation', 'Ur9en7! $h@re 0-T-P t0d4y 0r 4cc0un7 bl0ck3d!')
]

print("="*70)
print("Testing Enhanced Obfuscation Normalization")
print("="*70)

for name, text in obfuscation_tests:
    result = analyze_text(text)
    flag_count = sum(1 for v in result['flags'].values() if v and v != 'otp_notification_safe')
    
    print(f"\n{name}:")
    print(f"  Original: {text}")
    print(f"  Risk Level: {result['risk_level']} (Score: {result['risk_score']})")
    print(f"  Flags Detected: {flag_count}")
    
    detected = [k for k, v in result['flags'].items() if v and k != 'otp_notification_safe']
    if detected:
        print(f"  Active Flags: {', '.join(detected)}")

print("\n" + "="*70)
print("✅ All obfuscation tests complete")
print("="*70)
