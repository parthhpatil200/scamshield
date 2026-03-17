"""
Generate synthetic scam SMS messages covering 2026 threat patterns.

Covers 12 scam categories missing from existing training data:
  1.  Fake delivery / unpaid shipping fee (USPS, FedEx, DHL)
  2.  Toll fee scams (E-ZPass, SunPass, FASTag)
  3.  Wrong-number pig-butchering / investment grooming
  4.  Fake job / task-based scams
  5.  Boss gift-card impersonation
  6.  IRS / tax authority impersonation
  7.  Subscription auto-renewal scams
  8.  Overpayment / refund scams
  9.  Fake debt collector threats
 10.  Utility disconnection threats
 11.  Student loan forgiveness scams
 12.  Cryptocurrency investment scams

Output: data/raw/synthetic_scams_2026.csv  (columns: text, label — all label=1)
"""

import random
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _link():
    domains = [
        "bit.ly/3xR{n}aP", "tinyurl.com/scam{n}", "track-pkg.net/id={n}",
        "usps-delivery.info/pkg{n}", "amaz0n-verify.com/order{n}",
        "secure-portal.xyz/login{n}", "update-pay.net/ref{n}",
        "gov-relief.org/apply{n}", "irs-notice.com/case{n}",
        "loan-forgive.net/claim{n}", "crypto-gains.info/invest{n}",
        "verify-account.co/user{n}", "pay-toll.online/ref{n}",
        "ezpass-alert.net/pay{n}", "delivery-fee.info/track{n}",
    ]
    n = random.randint(10000, 99999)
    return random.choice(domains).format(n=n)


def _amount():
    return random.choice([
        1.25, 2.50, 3.25, 4.99, 5.00, 9.99, 12.50, 15.00,
        24.99, 35.00, 49.99, 50.00, 75.00, 99.00, 100.00,
    ])


def _big_amount():
    return random.randint(200, 5000)


def _phone():
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"


def _case():
    return f"CASE{random.randint(100000, 999999)}"


def _ref():
    return f"REF{random.randint(1000000, 9999999)}"


def _pkg():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choices(chars, k=12))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Fake Delivery / Unpaid Shipping Fee
# ─────────────────────────────────────────────────────────────────────────────

DELIVERY_TEMPLATES = [
    "USPS: Your package {pkg} is pending delivery. Pay a ${amt} shipping fee to release it: {link}",
    "FedEx Alert: Package {pkg} held at facility. Settle outstanding fee of ${amt} to proceed: {link}",
    "DHL Notice: Customs clearance required for parcel {pkg}. Pay ${amt} now: {link}",
    "Your package {pkg} could not be delivered. Update delivery address to avoid return: {link}",
    "USPS: Delivery failed. Reschedule and pay ${amt} redelivery fee here: {link}",
    "We tried delivering your parcel but couldn't reach you. Pay ${amt} to rebook: {link}",
    "Your shipment is on hold due to unpaid import duties of ${amt}. Pay now: {link}",
    "Amazon Logistics: Package {pkg} requires address confirmation. Verify immediately: {link}",
    "Delivery attempted for {pkg}. Pay small handling fee of ${amt} within 24 hours: {link}",
    "FedEx: Final attempt — pay ${amt} to release package {pkg} before it's returned: {link}",
    "DHL: Your parcel has been stopped at customs. Immediate payment of ${amt} required: {link}",
    "USPS ALERT: Undelivered item {pkg}. Confirm your address and pay ${amt}: {link}",
    "Package {pkg} delivery suspended. Pay ${amt} redelivery fee to resume: {link}",
    "Notice: Shipment detained. Inspection fee ${amt} required. Pay here: {link}",
    "Your order couldn't be delivered due to incorrect address. Click to update: {link}",
]


def gen_delivery(n):
    msgs = []
    for _ in range(n):
        t = random.choice(DELIVERY_TEMPLATES)
        msgs.append(t.format(pkg=_pkg(), amt=round(_amount(), 2), link=_link()))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 2. Toll Fee Scams
# ─────────────────────────────────────────────────────────────────────────────

TOLL_TEMPLATES = [
    "E-ZPass: Unpaid toll of ${amt}. Avoid penalties — pay now: {link}",
    "SunPass Alert: Outstanding toll balance of ${amt}. Pay before {date} to avoid fines: {link}",
    "FASTag Notice: Your vehicle has an unpaid toll of Rs {inr}. Pay immediately: {link}",
    "NHAI: Toll due Rs {inr}. Failure to pay within 24 hrs will result in legal action: {link}",
    "E-ZPass: Your account has a past-due balance of ${amt}. Settle now: {link}",
    "SunPass: Final notice — pay ${amt} toll fee or face a ${fine} penalty: {link}",
    "Toll authority: Your license plate was recorded with unpaid toll. Pay ${amt}: {link}",
    "E-ZPass URGENT: Overdue toll charges ${amt} on your account. Avoid suspension: {link}",
    "Toll violation notice: Pay ${amt} within 48 hours to avoid additional fees of ${fine}: {link}",
    "FASTag: Wallet balance low. Unpaid toll Rs {inr} detected. Recharge now: {link}",
    "Your toll bill of ${amt} is overdue. Pay online to avoid late charges: {link}",
    "SunPass: Account suspended due to unpaid tolls. Pay ${amt} to restore: {link}",
]


def gen_toll(n):
    def _inr():
        return random.randint(50, 500)
    def _fine():
        return random.choice([25, 50, 75, 100])
    def _date():
        days = ["tomorrow", "within 24 hours", "today", "in 48 hours"]
        return random.choice(days)

    msgs = []
    for _ in range(n):
        t = random.choice(TOLL_TEMPLATES)
        msgs.append(t.format(amt=round(_amount(), 2), inr=_inr(),
                             fine=_fine(), link=_link(), date=_date()))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 3. Wrong-Number Pig-Butchering / Investment Grooming
# ─────────────────────────────────────────────────────────────────────────────

INVESTMENT_GROOMING_TEMPLATES = [
    "Hi, is this {name}? Sorry wrong number! But since you replied — I trade crypto and made ${profit}K last month. Interested?",
    "Hey sorry wrong number! I'm Linda, wealth advisor. I help people earn passive income. Want to know how?",
    "Hi! Mistaken number, sorry. Are you into investments? I just made ${profit}K using an AI trading platform.",
    "Wrong number, my bad! But you sound smart — have you heard about {coin}? I turned $500 into ${profit}K. DM me.",
    "Hi {name}? Oops, wrong contact! By the way, I've been earning daily from crypto signals. Want the link?",
    "Sorry wrong number! But since we're talking — my mentor's platform gives 15% weekly returns. Try it: {link}",
    "Hi, looking for {name}. Never mind! Do you invest? I know a platform with guaranteed 20% monthly returns.",
    "Oops wrong number! I'm an investment advisor. Our fund returned 300% last year. Curious? Reply YES.",
    "Hey wrong number! I manage a crypto portfolio. Want to see my returns? I can help you start with just $100.",
    "Hi, meant to text someone else. While here — ever heard of {coin}? It's about to 10x. Get in early: {link}",
]


def gen_investment_grooming(n):
    names = ["Alex", "James", "Sofia", "Michael", "Emma", "David", "Sarah", "Nina", "Robert", "Amy"]
    coins = ["Bitcoin", "Ethereum", "USDT arbitrage", "BNB Coin", "XRP"]
    msgs = []
    for _ in range(n):
        t = random.choice(INVESTMENT_GROOMING_TEMPLATES)
        msgs.append(t.format(
            name=random.choice(names),
            profit=random.randint(5, 200),
            coin=random.choice(coins),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 4. Fake Job / Task Scams
# ─────────────────────────────────────────────────────────────────────────────

JOB_TASK_TEMPLATES = [
    "Congratulations! You've been selected for a remote task role. Earn ${daily}/day rating hotels. Start today!",
    "Hiring now: App reviewers needed. Earn ${daily}–${daily2}/hr from home. No experience required. Apply: {link}",
    "Work from home opportunity! Complete simple tasks online, earn ${weekly}/week. Registration open: {link}",
    "You have been shortlisted for a micro-task job. Earn ${daily} daily. Training provided. Join now: {link}",
    "Part-time online work available. Rate products, earn real money. Daily payout. Sign up: {link}",
    "Our company is hiring remote content reviewers. Flexible hours, earn ${daily}/task. Apply here: {link}",
    "Task job available: Like videos and earn ${weekly}/week. First task is free — join our team: {link}",
    "Work from home! Get paid ${daily} per day to complete easy online surveys. No experience needed: {link}",
    "You're invited to join our review platform. Earn ${daily}/hr reviewing Amazon products. Register: {link}",
    "Easy remote tasks — earn up to ${weekly}/week in your spare time. No investment needed. Start: {link}",
    "Join our task platform and earn daily. Your first payout is guaranteed after 3 tasks. Sign up: {link}",
    "We are recruiting 50 home-based workers. Earn ${daily} per day completing micro tasks. Apply: {link}",
]


def gen_job_task(n):
    msgs = []
    for _ in range(n):
        t = random.choice(JOB_TASK_TEMPLATES)
        d = random.randint(50, 300)
        msgs.append(t.format(
            daily=d, daily2=d + random.randint(50, 100),
            weekly=d * random.randint(5, 7),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 5. Boss Gift-Card Impersonation
# ─────────────────────────────────────────────────────────────────────────────

BOSS_GIFTCARD_TEMPLATES = [
    "Hi it's {boss}. I need you to buy ${amt} in Amazon gift cards for a client. Send me the codes ASAP.",
    "This is {boss}, I'm in a meeting. Can you grab ${amt} in Google Play gift cards? I'll reimburse you today.",
    "Hey, {boss} here. Urgent favor — buy ${amt} iTunes gift cards and text me the redemption codes.",
    "Hi, it's {boss}. I need gift cards for a vendor. Buy 2x ${card_amt} Amazon cards and send codes now.",
    "From {boss}: I need you to purchase ${amt} Steam gift cards urgently. Keep it confidential for now.",
    "This is {boss}. I'm tied up in meetings. Can you get ${amt} in gift cards? Very important for a client deal.",
    "Hi — {boss} here. Need ${amt} in Apple gift cards immediately. Purchase and send codes to this number.",
    "{boss}: Need a favor. Buy ${card_amt} x {qty} Google gift cards and send codes. I'll pay you back.",
    "It's {boss}. Can you please buy some gift cards for me? ${amt} total. Text me the codes when done.",
    "This is {boss} — board meeting running late. Buy ${amt} Amazon gift cards and email me the codes urgently.",
]


def gen_boss_giftcard(n):
    bosses = [
        "your CEO", "Mr. Johnson", "Sarah (Director)", "the MD", "your manager",
        "CEO Mike", "Dr. Patel", "your supervisor", "the GM", "Regional Head Raj",
    ]
    msgs = []
    for _ in range(n):
        t = random.choice(BOSS_GIFTCARD_TEMPLATES)
        card_amt = random.choice([25, 50, 100, 200])
        qty = random.randint(2, 5)
        msgs.append(t.format(
            boss=random.choice(bosses),
            amt=card_amt * qty,
            card_amt=card_amt,
            qty=qty,
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 6. IRS / Tax Authority Impersonation
# ─────────────────────────────────────────────────────────────────────────────

IRS_TAX_TEMPLATES = [
    "IRS Notice: Outstanding tax liability of ${amt}. Immediate payment required to avoid arrest: {link}",
    "IRS: You have an unpaid tax of ${amt}. Pay now or face legal proceedings: {phone}",
    "Final IRS notice — failure to respond within 24 hours will result in account levy: {link}",
    "Income Tax Dept: Your PAN {pan} has a pending demand of Rs {inr}. Respond now: {link}",
    "IRS Alert: Case {case} — warrant issued. Call {phone} immediately to avoid arrest.",
    "Tax Authority: Your account has been flagged for audit. Settle ${amt} to close the case: {link}",
    "IRS: Refund of ${amt} pending. Claim your refund before it expires: {link}",
    "CBDT Notice: TDS default detected. Pay Rs {inr} penalty immediately to avoid prosecution: {link}",
    "Income Tax: You owe ${amt} in back taxes. Failure to pay will result in wage garnishment.",
    "IRS URGENT: Tax fraud detected on your SSN. Call {phone} within 24 hours or face arrest.",
    "GST Authority: Non-compliance notice for business reg {case}. Pay penalty Rs {inr}: {link}",
    "Tax dept: Your return filing is overdue. Pay ${amt} fine now to avoid criminal charges: {link}",
]


def gen_irs_tax(n):
    def _pan():
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return f"{''.join(random.choices(chars, k=5))}{random.randint(1000,9999)}{''.join(random.choices(chars, k=1))}"

    msgs = []
    for _ in range(n):
        t = random.choice(IRS_TAX_TEMPLATES)
        msgs.append(t.format(
            amt=_big_amount(), inr=random.randint(5000, 50000),
            case=_case(), phone=_phone(), link=_link(),
            pan=_pan(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 7. Subscription Auto-Renewal Scams
# ─────────────────────────────────────────────────────────────────────────────

SUBSCRIPTION_TEMPLATES = [
    "Your Netflix subscription will auto-renew for ${amt} today. Cancel now to avoid charges: {link}",
    "Amazon Prime: Your membership renews at ${amt}/year in 24 hours. Cancel here: {link}",
    "McAfee subscription renewal notice: ${amt} will be charged. To cancel call {phone} or click: {link}",
    "Your Norton antivirus renews today for ${amt}. Cancel subscription immediately: {link}",
    "Disney+ Alert: Annual plan of ${amt} will be auto-charged. To opt out: {link}",
    "Spotify: Your Premium plan renews at ${amt} on {date}. Cancel before renewal: {link}",
    "Apple: Your iCloud subscription of ${amt}/month will renew automatically. Manage: {link}",
    "Adobe Creative Cloud: Renewal of ${amt} scheduled. Cancel to avoid charge: {link}",
    "Your antivirus subscription is set to renew at ${amt}. Stop auto-renewal: {link}",
    "Hulu alert: ${amt} will be charged to your card ending in {card} for annual renewal: {link}",
    "Microsoft 365 renewal: ${amt} will be billed in 24 hours. Cancel here: {link}",
    "Your streaming plan renews at ${amt} tomorrow. To stop automatic billing: {link}",
]


def gen_subscription(n):
    def _date():
        return random.choice(["tomorrow", "today", "in 24 hours", "in 48 hours", "on 03/18/2026"])
    def _card():
        return random.randint(1000, 9999)

    msgs = []
    for _ in range(n):
        t = random.choice(SUBSCRIPTION_TEMPLATES)
        msgs.append(t.format(
            amt=random.choice([4.99, 7.99, 9.99, 12.99, 14.99, 29.99, 49.99, 99.00, 119.99]),
            date=_date(), card=_card(), phone=_phone(), link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 8. Overpayment / Refund Scams
# ─────────────────────────────────────────────────────────────────────────────

REFUND_TEMPLATES = [
    "You've overpaid ${amt} on your recent order. Click to receive your refund: {link}",
    "Customer refund pending: ${amt} is waiting to be credited to your account. Claim: {link}",
    "We owe you a refund of ${amt}. Verify your bank details to receive it: {link}",
    "Tax refund of ${amt} approved for your account. Claim before {date}: {link}",
    "Your refund of Rs {inr} for cancelled order is ready. Enter bank details to receive: {link}",
    "Excess payment of ${amt} detected. To process your refund immediately: {link}",
    "Refund notice: ${amt} from your last transaction is being returned. Confirm account: {link}",
    "You are eligible for a ${amt} government rebate. Submit your details here: {link}",
    "Cashback of Rs {inr} from your recent purchase is ready. Claim via: {link}",
    "Your insurance overpayment refund of ${amt} is awaiting collection. Act now: {link}",
    "Telecom refund: Rs {inr} credited due to billing error. Verify to receive: {link}",
    "Refund ${amt} has been initiated but requires your bank confirmation: {link}",
]


def gen_refund(n):
    msgs = []
    for _ in range(n):
        t = random.choice(REFUND_TEMPLATES)
        msgs.append(t.format(
            amt=round(random.uniform(20, 500), 2),
            inr=random.randint(500, 10000),
            date=random.choice(["48 hours", "3 days", "today", "this week"]),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 9. Fake Debt Collector Threats
# ─────────────────────────────────────────────────────────────────────────────

DEBT_COLLECTOR_TEMPLATES = [
    "FINAL NOTICE: You owe ${amt} on account {ref}. Legal action will begin in 24 hours. Call {phone}.",
    "Debt collection agency: Overdue balance of ${amt}. Pay now to avoid court proceedings: {link}",
    "This is your last chance to pay ${amt} before we refer your case to our legal team: {phone}",
    "Outstanding debt of ${amt} — warrant for your arrest has been filed. Call immediately: {phone}",
    "Collection notice: Your unpaid loan of ${amt} is being sent to litigation. Settle now: {link}",
    "URGENT: ${amt} overdue on your account. Resolve immediately to protect your credit score: {link}",
    "Debt recovery: Final demand for ${amt}. Ignore this and face court summons. Contact us: {phone}",
    "Notice of default: ${amt} past due. Failure to respond will result in civil lawsuit: {link}",
    "${amt} debt on file for {ref}. Wage garnishment will begin if not resolved today: {phone}",
    "Legal dept: Your unpaid balance of ${amt} is being escalated. Settle to avoid litigation: {link}",
    "Final warning: Pay ${amt} by end of day or your account will be forwarded to attorneys: {phone}",
    "Debt alert: ${amt} overdue. Your credit will be severely impacted. Pay now: {link}",
]


def gen_debt_collector(n):
    msgs = []
    for _ in range(n):
        t = random.choice(DEBT_COLLECTOR_TEMPLATES)
        msgs.append(t.format(
            amt=_big_amount(), ref=_ref(), phone=_phone(), link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 10. Utility Disconnection Threats
# ─────────────────────────────────────────────────────────────────────────────

UTILITY_TEMPLATES = [
    "Your electricity service will be disconnected in 2 hours due to non-payment. Pay Rs {inr} now: {link}",
    "BESCOM: Pending bill of Rs {inr}. Disconnection scheduled today. Pay immediately: {link}",
    "Gas utility: Overdue balance of ${amt}. Service will be cut off today. Pay: {link}",
    "Power company: Final notice — pay ${amt} now or your service will be disconnected in 1 hour.",
    "Water board: Outstanding bill Rs {inr}. Supply will be halted unless paid immediately: {link}",
    "Electricity dept: Your connection will be terminated due to unpaid Rs {inr}. Pay here: {link}",
    "URGENT — your gas connection will be suspended in 3 hours. Pay ${amt} to avoid disconnection: {link}",
    "Your electric bill is past due. Pay ${amt} in the next hour or service will be interrupted: {link}",
    "Utility Alert: Disconnect order issued for your address. Pay overdue Rs {inr} now: {link}",
    "Cable/internet will be shut off today due to non-payment of ${amt}. Pay now: {link}",
    "TATA Power: Disconnect notice for unpaid dues Rs {inr}. Immediate payment required: {link}",
    "Final disconnect warning: Settle ${amt} in the next 2 hours to keep your service active: {link}",
]


def gen_utility(n):
    msgs = []
    for _ in range(n):
        t = random.choice(UTILITY_TEMPLATES)
        msgs.append(t.format(
            inr=random.randint(500, 5000),
            amt=round(random.uniform(50, 300), 2),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 11. Student Loan Forgiveness Scams
# ─────────────────────────────────────────────────────────────────────────────

STUDENT_LOAN_TEMPLATES = [
    "Your student loan forgiveness application has been approved. Confirm details before benefits expire: {link}",
    "Federal loan relief: You qualify for ${amt} in student loan cancellation. Enroll now: {link}",
    "URGENT: Student loan forgiveness deadline is today. Submit your information now: {link}",
    "Education Dept: Your loan of ${amt} is eligible for 100% forgiveness. Apply: {link}",
    "Final notice: Student loan discharge approved. Provide SSN to process your ${amt} forgiveness: {link}",
    "Limited time: New government program forgives up to ${amt} in student loans. Qualify here: {link}",
    "Your ${amt} student debt qualifies for immediate relief under the 2026 relief act. Claim: {link}",
    "Student loan update: Your ${amt} balance may be eligible for forgiveness. Act before deadline: {link}",
    "Loan servicer: ${amt} forgiveness benefit is being processed. Verify your FSA ID to continue: {link}",
    "Important: You must confirm your student loan details to receive ${amt} debt cancellation: {link}",
]


def gen_student_loan(n):
    msgs = []
    for _ in range(n):
        t = random.choice(STUDENT_LOAN_TEMPLATES)
        msgs.append(t.format(
            amt=random.choice([5000, 10000, 15000, 20000, 25000, 50000]),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# 12. Cryptocurrency Investment Scams
# ─────────────────────────────────────────────────────────────────────────────

CRYPTO_TEMPLATES = [
    "{coin} is about to explode. Insiders are buying now. Get in before it's too late: {link}",
    "Earn 15% weekly returns guaranteed. Our AI crypto bot never loses. Start with $100: {link}",
    "Exclusive: My trading signal made ${profit}K last month. Join our VIP group: {link}",
    "URGENT: {coin} pump alert. Invest now to 10x your money in 30 days: {link}",
    "Guaranteed crypto profits — verified track record of {pct}% monthly ROI. Join: {link}",
    "Bitcoin arbitrage opportunity: Turn ${seed} into ${profit}K with zero risk. Learn how: {link}",
    "Our members earned ${profit}K in the last 7 days trading {coin}. Join free: {link}",
    "Celebrity endorsed crypto platform — Elon Musk uses it to earn ${profit} daily. Try: {link}",
    "Crypto recovery service: Lost money in scams? We can recover ${profit}K for you. Contact: {link}",
    "Last chance — {coin} presale ends tonight. Buy now before 100x launch: {link}",
    "Top hedge funds are quietly buying {coin}. Get in before the surge. Invest ${seed}: {link}",
    "AI trading bot — {pct}% profit in 24 hours, fully automated. Register free: {link}",
]


def gen_crypto(n):
    coins = [
        "Bitcoin", "Ethereum", "BNB", "XRP", "Solana", "DOGE",
        "SHIBA INU", "PEPE coin", "a new altcoin", "this token",
    ]
    msgs = []
    for _ in range(n):
        t = random.choice(CRYPTO_TEMPLATES)
        msgs.append(t.format(
            coin=random.choice(coins),
            profit=random.randint(5, 500),
            seed=random.choice([50, 100, 200, 500, 1000]),
            pct=random.randint(15, 300),
            link=_link(),
        ))
    return msgs


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_GENERATORS = {
    "fake_delivery":          (gen_delivery,            500),
    "toll_fee":               (gen_toll,                500),
    "investment_grooming":    (gen_investment_grooming, 500),
    "fake_job_task":          (gen_job_task,            500),
    "boss_giftcard":          (gen_boss_giftcard,       500),
    "irs_tax":                (gen_irs_tax,             500),
    "subscription_renewal":   (gen_subscription,        500),
    "refund_overpayment":     (gen_refund,              500),
    "debt_collector":         (gen_debt_collector,      500),
    "utility_threat":         (gen_utility,             500),
    "student_loan":           (gen_student_loan,        500),
    "crypto_investment":      (gen_crypto,              500),
}


def main():
    print("=" * 60)
    print("ScamShield — 2026 Synthetic Scam Data Generator")
    print("=" * 60)

    all_messages = []
    for category, (fn, count) in CATEGORY_GENERATORS.items():
        msgs = fn(count)
        all_messages.extend(msgs)
        print(f"  ✅  {category:<25} {len(msgs):>4} messages")

    random.shuffle(all_messages)

    df = pd.DataFrame({
        "text": all_messages,
        "label": 1,
    })

    # Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    print(f"\n  Removed {before - len(df)} duplicates")
    print(f"  Final count: {len(df)} scam messages")

    output_path = Path(__file__).parent / "data" / "raw" / "synthetic_scams_2026.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n✅ Saved to: {output_path}")
    print("=" * 60)
    print("\nSample messages:")
    for msg in df["text"].sample(10, random_state=42).tolist():
        print(f"  - {msg}")


if __name__ == "__main__":
    main()
