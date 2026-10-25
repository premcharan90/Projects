from email import policy
from email.parser import BytesParser
import re

FILE = r"evidence\suspicious_email.eml"
OUTPUT = r"iocs\extracted_iocs.txt"

with open(FILE, "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)

# Extract URLs from all text parts
urls = []

for part in msg.walk():
    if part.get_content_type() in ("text/plain", "text/html"):
        try:
            body = part.get_content()
        except Exception:
            continue

        urls.extend(re.findall(r'https?://[^\s<>"\']+', body))

# Remove duplicates while preserving order
urls = list(dict.fromkeys(urls))

# Extract IPv4 addresses from Received headers
received_headers = msg.get_all("Received", [])
ips = []

for header in received_headers:
    ips.extend(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', header))

ips = list(dict.fromkeys(ips))

# Extract domains from email addresses
email_headers = [
    msg["From"],
    msg["Reply-To"],
    msg["Return-Path"],
    msg["Message-ID"]
]

domains = []

for header in email_headers:
    if header:
        matches = re.findall(r'@([A-Za-z0-9.-]+\.[A-Za-z]{2,})', header)
        domains.extend(matches)

domains = list(dict.fromkeys(domains))

# Write IOC report
with open(OUTPUT, "w", encoding="utf-8") as f:

    f.write("=== EXTRACTED IOCs ===\n\n")

    f.write("[EMAIL ADDRESSES]\n")
    f.write(f"From: {msg['From']}\n")
    f.write(f"Reply-To: {msg['Reply-To']}\n")
    f.write(f"Return-Path: {msg['Return-Path']}\n")

    f.write("\n[IP ADDRESSES]\n")
    for ip in ips:
        f.write(f"{ip}\n")

    f.write("\n[DOMAINS]\n")
    for domain in domains:
        f.write(f"{domain}\n")

    f.write("\n[URLS]\n")
    for url in urls:
        f.write(f"{url}\n")

    f.write("\n[AUTHENTICATION RESULTS]\n")
    f.write(f"{msg['Authentication-Results']}\n")

print(f"IOC extraction complete.")
print(f"Output saved to: {OUTPUT}")