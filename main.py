from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

from otp_reader import erp_otp

# Load credentials from environment
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ERP_USER_ID = os.getenv("ERP_USER_ID")
ERP_PASSWORD = os.getenv("ERP_PASSWORD")

# Load security answers from environment
answers = {
    os.getenv("Q1"): os.getenv("A1"),
    os.getenv("Q2"): os.getenv("A2"),
    os.getenv("Q3"): os.getenv("A3")
}

if not all([EMAIL, EMAIL_PASSWORD, ERP_USER_ID, ERP_PASSWORD]):
    raise Exception("Please set all credentials in the .env file")

if not all(answers.values()):
    raise Exception("Please set all security question answers in the .env file")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

# STEP 1: Open base login page (NO token)
driver.get("https://erp.iitkgp.ac.in/")

# STEP 2: Fill credentials
wait.until(EC.presence_of_element_located((By.ID, "user_id"))).send_keys(ERP_USER_ID)
driver.find_element(By.ID, "password").send_keys(ERP_PASSWORD)

# STEP 3: Wait for security question to appear
question_elem = WebDriverWait(driver, 30).until(
    lambda d: d.find_element(By.ID, "question") if d.find_element(By.ID, "question").text.strip() != "" else False
)

question = question_elem.text.strip()
print("Security question detected:", repr(question))

# STEP 3.1: Fill the answer from .env
driver.find_element(By.ID, "answer").send_keys(answers[question])
driver.find_element(By.ID, "getotp").click()

# STEP 3.2: Handle OTP alert popup
try:
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    print("Alert detected:", alert.text)
    alert.accept()  # Automatically clicks OK
    print("Alert accepted.")
except:
    print("No alert appeared.")

# STEP 4: Wait and fetch OTP with retries
otp = None
max_retries = 15
retry_delay =1

print("Waiting for OTP from email...")
otp = erp_otp(EMAIL, EMAIL_PASSWORD)


# STEP 5: Enter OTP and submit
driver.find_element(By.ID, "email_otp1").send_keys(otp)
driver.find_element(By.ID, "loginFormSubmitButton").click()

input("Press Enter to close the browser...")
driver.quit()
