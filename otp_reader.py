import imaplib
import email
import re
from email.header import decode_header
import time
import os
from dotenv import load_dotenv


load_dotenv()


def erp_otp(email_address=None, password=None, imap_server=None):
    """Read OTP using IMAP protocol"""
    try:
        # Allow environment variables to provide defaults
        if email_address is None:
            email_address = os.getenv("EMAIL")
        if password is None:
            password = os.getenv("EMAIL_PASSWORD")
        if imap_server is None:
            imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        # Search for unread emails in last 1 minutes
        date_since = time.strftime("%d-%b-%Y", time.localtime(time.time() - 300))
        result, data = mail.search(None, f'(UNSEEN SINCE {date_since})')

        if result != 'OK':
            return "No new emails"

        email_ids = data[0].split()

        if not email_ids:
            return "No unread emails found"

        # Get the latest email
        latest_email_id = email_ids[-1]
        result, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        if result != 'OK':
            return "Failed to fetch email"

        # Parse email
        msg = email.message_from_bytes(msg_data[0][1])

        # Get sender and subject
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        print(f"Checking email from: {msg['From']}")
        print(f"Subject: {subject}")

        # Extract OTP from email body
        otp = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    otp = extract_otp(body)
                    break
        else:
            body = msg.get_payload(decode=True).decode()
            otp = extract_otp(body)

        # Mark as read
        mail.store(latest_email_id, '+FLAGS', '\\Seen')

        mail.close()
        mail.logout()

        return otp if otp else "No OTP found"

    except Exception as e:
        return f"Error: {str(e)}"


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