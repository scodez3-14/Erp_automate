# Erp_automate

Small automation to login to the IIT KGP ERP site using Selenium and automatically fetch the email OTP via IMAP.

This project contains two main scripts:

- `main.py` — Selenium automation to open the ERP login page, fill credentials, answer the security question, request an OTP, poll the email inbox and submit the OTP.
- `otp_reader.py` — IMAP-based helper that connects to an email account and extracts OTP codes from recent unread messages.


## Requirements

- Python 3.8+
- Chrome (or Chromium) and a matching Chromedriver for Selenium.
- Python packages (install with pip):
  - python-dotenv
  - selenium

If you want a quick starter requirements file, create one with:

```
python-dotenv
selenium
```

## Setup

1. Create a `.env` file in the project root with the required environment variables. Example:

```env
# Email account used to receive OTPs
EMAIL=you@example.com
EMAIL_PASSWORD=your_imap_app_password
IMAP_SERVER=imap.gmail.com

# ERP credentials
USER_ID=24XXXXXX
USER_PASSWORD=XXXXXXX

# Security question answers (exact text must match the site question)
Q1=XXXXXXXXXXX
A1=XXX

Q2=XXXXXXXXXXXXX
A2=YYYYY

Q3=XXXXXXXXXXXXXXXX
A3=YYYYYYq

----BE CAREFUL WRITE EXACT SAME QUES OF YOURS , THIS ARE JUST EXAMPLE----

# Optional: OTP polling behavior
OTP_MAX_RETRIES=10
OTP_RETRY_DELAY=2
```

Notes:
- For Gmail/Google accounts, use an App Password for IMAP (if you have 2FA) and ensure IMAP access is enabled for the account.
## Usage

- To test the OTP reader alone:

```bash
python otp_reader.py
```

- To run the full automation (this will open Chrome and perform the login flow):

```bash
python main.py
```

Be present when running `main.py` because it opens a browser and will interact with visible elements. The script will ask you to press Enter to quit the browser after completing the flow.

LINSENCE :XD
