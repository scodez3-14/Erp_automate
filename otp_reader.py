import imaplib
import email
import re
import time
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

def erp_otp(email_address=None, password=None, timeout=120):
    start_time = datetime.datetime.now(datetime.timezone.utc)
    email_address = email_address or os.getenv("EMAIL")
    password = password or os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

    print(f"Waiting for OTP (Started at {start_time.strftime('%H:%M:%S')})...")

    end_period = time.time() + timeout
    
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        
        while time.time() < end_period:
            mail.select("inbox")
            subject_filter = 'OTP for Sign In in ERP Portal of IIT Kharagpur'
            # Search for both UNSEEN and SEEN just in case, then filter by time
            result, data = mail.search(None, f'(SUBJECT "{subject_filter}")')

            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                # Iterate from newest to oldest
                for msg_id in reversed(email_ids):
                    _, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    date_str = msg.get("Date")
                    email_dt = email.utils.parsedate_to_datetime(date_str)
                    
                    # Ensure it's a fresh email from this session
                    if email_dt > start_time:
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                        else:
                            body = msg.get_payload(decode=True).decode()

                        otp = extract_otp(body)
                        if otp:
                            print(f"OTP found: {otp}")
                            # SUCCESS: Now mark as read
                            mail.store(msg_id, '+FLAGS', '\\Seen')
                            mail.logout()
                            return otp
            
            print("OTP not arrived yet. Retrying in 2 seconds...")
            time.sleep(1)
            
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

    return "Timeout: OTP did not arrive in time."

def extract_otp(text):
    """Refined extraction with a fallback for IIT KGP specific text"""
    patterns = [
        r'(\d{6})', # Usually KGP uses 6 digits
        r'OTP is\s*(\d{4,8})',
        r'verification code is\s*(\d{4,8})'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

if __name__ == "__main__":
    otp = erp_otp()
    print(f"Final Result: {otp}")