from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
import re

FILE = r"evidence\suspicious_email.eml"

with open(FILE, "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)

print("=== EMAIL HEADER ANALYSIS ===")
print("From:", msg["From"])
print("Reply-To:", msg["Reply-To"])
print("Return-Path:", msg["Return-Path"])
print("To:", msg["To"])
print("Subject:", msg["Subject"])
print("Date:", msg["Date"])
print("Message-ID:", msg["Message-ID"])

print("\n=== AUTHENTICATION RESULTS ===")
print(msg["Authentication-Results"])

print("\n=== RECEIVED HEADERS ===")
for header in msg.get_all("Received", []):
    print(header)

print("\n=== URL EXTRACTION ===")

urls = []

for part in msg.walk():
    if part.get_content_type() in ("text/plain", "text/html"):
        try:
            body = part.get_content()
        except Exception:
            continue

        found = re.findall(r'https?://[^\s<>"\']+', body)
        urls.extend(found)

for url in urls:
    print(url)

print("\n=== ANALYSIS COMPLETE ===")