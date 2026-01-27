import json
import random
from datetime import datetime, timedelta
import re
import string

# -------------------------------
mandates = [
    "Netflix", "Amazon Prime", "Spotify", "Disney+ Hotstar", "YouTube Premium",
    "Zomato", "Swiggy", "PhonePe", "Paytm", "Google One", "Airtel", "Jio",
    "Apple Music", "LinkedIn Premium", "Udemy", "Coursera", "Tata Play", "Hulu",
    "Zoom", "Dropbox", "Gaana", "SonyLIV", "MX Player", "BookMyShow", "Hotstar VIP",
    "Netflix Kids", "Flipkart Plus", "Ola Money", "Uber", "RedBus", "Revv",
    "Byju's", "Unacademy", "Groww", "Smallcase", "Razorpay", "Cred", "MoneyTap",
    "PhonePe Super App", "Amazon Pay", "HDFC Life", "ICICI Prudential", "Bajaj Finserv",
    "PayU", "Mobikwik", "Zerodha", "Upstox", "Kotak Mahindra", "Axis Bank", "HDFC Bank", "ICICI Bank"
]

banks = ["HDFC", "ICICI", "SBI", "Axis", "Kotak", "Yes Bank", "PNB", "IDFC First"]
status_options = ["pause", "unpaused", "revoke/cancel"]
frequencies = ["Daily", "Weekly", "Monthly"]

phone_numbers = [
    "9876543210", "9123456789", "8765432109", "7654321098", "9988776655",
    "8877665544", "7766554433", "9876512345", "8765123456", "7654234567"
]

# -------------------------------
def normalize(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", name.upper())[:10]

def short_uid(length=3):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_mandate_id(name: str, phone: str) -> str:
    return f"{normalize(name)}-{phone[-4:]}-{short_uid(3)}"

# -------------------------------
demo_data = []

for _ in range(50):
    mandate = random.choice(mandates)
    phone = random.choice(phone_numbers)

    record = {
        "mandate_id": generate_mandate_id(mandate, phone),   # ✅ PHONE-LINKED UNIQUE ID
        "mandate_name": mandate,
        "bank": random.choice(banks),
        "amount": round(random.uniform(100, 5000), 2),
        "status": random.choice(status_options),
        "execution_date": (
            datetime.now() + timedelta(days=random.randint(1, 30))
        ).strftime("%Y-%m-%d"),
        "execution_frequency": random.choice(frequencies),
        "phone_no": phone
    }

    demo_data.append(record)

# -------------------------------
FILE_NAME = "upi_mandates.json"

with open(FILE_NAME, "w", encoding="utf-8") as f:
    json.dump(demo_data, f, indent=4)

print(f"Saved 50 demo UPI mandates to '{FILE_NAME}'")
