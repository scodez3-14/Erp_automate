import imaplib
import email
import re
from email.header import decode_header
import time
import os
from dotenv import load_dotenv


load_dotenv()


import datetime

def erp_otp(email_address=None, password=None, timeout=120):
    """
    Polls the inbox for a NEW OTP email specifically from IIT KGP.
    timeout: max seconds to wait (default 2 minutes)
    """
    # 1. Record the exact time we started looking
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    email_address = email_address or os.getenv("EMAIL")
    password = password or os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

    print(f"Waiting for OTP (Started at {start_time.strftime('%H:%M:%S')})...")

    end_period = time.time() + timeout
    while time.time() < end_period:
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_address, password)
            mail.select("inbox")

            # Search for unread emails with the specific subject
            subject_filter = 'OTP for Sign In in ERP Portal of IIT Kharagpur'
            result, data = mail.search(None, f'(UNSEEN SUBJECT "{subject_filter}")')

            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                
                # Check the latest unread email
                latest_id = email_ids[-1]
                _, msg_data = mail.fetch(latest_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 2. Check the 'Date' header to ensure it's "Fresh"
                date_str = msg.get("Date")
                email_dt = email.utils.parsedate_to_datetime(date_str)
                
                if email_dt > start_time:
                    # This is the NEW one!
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()

                    otp = extract_otp(body)
                    print(f"OTP found: {otp}")
                    mail.store(latest_id, '+FLAGS', '\\Seen') # Mark read
                    mail.logout()
                    return otp
            
            mail.logout()
        except Exception as e:
            print(f"Error during poll: {e}")

        print("OTP not arrived yet. Retrying in 1 seconds...")
        time.sleep(1)

    return "Timeout: OTP did not arrive in time."


def extract_otp(text):
    """Extract OTP from text using regex patterns"""
    patterns = [
        r'\b\d{4,8}\b',
        r'OTP[:\s]*(\d{4,8})',
        r'One[\s-]*Time[\s-]*Password[:\s]*(\d{4,8})',
        r'Verification[\s-]*Code[:\s]*(\d{4,8})',
        r'code[\s]*:[\s]*(\d{4,8})',
        r'(\d{4,8})[\s]*is your OTP'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if len(match) >= 4:  # Minimum OTP length
                return match

    return None


if __name__ == "__main__":
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL or not PASSWORD:
        print("EMAIL and EMAIL_PASSWORD must be set in the environment or .env file")
    else:
        otp = erp_otp(EMAIL, PASSWORD)
        print(f"Latest OTP: {otp}")