import requests, json, random, string, time, os, sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

API_URL = os.getenv("TEMPMail_API_URL")
TOKEN = os.getenv("TEMPMail_TOKEN")
DOMAIN = os.getenv("TEMPMail_DOMAIN")
CALLBACK_URL = os.getenv("CALLBACK_URL")
CALLBACK_SECRET = os.getenv("CALLBACK_SECRET")

def chrome_options():
    opts = uc.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return opts

def random_username(prefix="arcgis"):
    return f"{prefix}{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

def random_password():
    chars = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choices(chars, k=10))

def create_temp_email():
    headers = {'Authorization': TOKEN, 'Content-Type': 'application/json'}
    user = f"{random.choice(['nguyen','tran','le','pham','hoang','vo','bui'])}{random.randint(100,9999)}"
    payload = json.dumps({"user": user, "domain": DOMAIN})
    r = requests.post(API_URL, headers=headers, data=payload).json()
    if not r.get("success"):
        raise Exception(f"TempMail create failed: {r}")
    return user, f"{user}@{DOMAIN}"

def register_arcgis(email_user, email_full):
    driver = uc.Chrome(options=chrome_options(), use_subprocess=True)
    wait = WebDriverWait(driver, 30)
    driver.get("https://www.esri.com/en-us/arcgis/products/arcgis-online/trial/sign-up")

    try:
        btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        driver.execute_script("arguments[0].click();", btn)
    except: pass

    driver.find_element(By.CSS_SELECTOR, "input[aria-label='First Name']").send_keys("Nguyen")
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Last Name']").send_keys("Truc")
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Business Email']").send_keys(email_full)
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Company']").send_keys("NghienPlus")
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Department']").send_keys("IT")
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Job Title']").send_keys("Developer")

    Select(driver.find_element(By.NAME, "org_type")).select_by_visible_text("Education")
    Select(driver.find_element(By.NAME, "industry")).select_by_visible_text("Higher Education")
    Select(driver.find_element(By.NAME, "country")).select_by_visible_text("Viet Nam")

    driver.find_element(By.NAME, "phone_tel").send_keys("0123456789")

    for cid in ["contactConsent", "marketingConsent"]:
        try:
            el = driver.find_element(By.ID, cid)
            driver.execute_script("arguments[0].checked = true;", el)
        except: pass

    driver.find_element(By.CSS_SELECTOR, "span.submit-button-label").click()
    time.sleep(10)
    driver.quit()
    print("✅ Registered ArcGIS trial")

def post_back(username, password, email):
    if not CALLBACK_URL:
        print(json.dumps({"username": username, "password": password, "email": email}))
        return
    headers = {"Authorization": f"Bearer {CALLBACK_SECRET}", "Content-Type": "application/json"}
    payload = {"username": username, "password": password, "email": email}
    try:
        r = requests.post(CALLBACK_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        print("✅ Posted credentials to callback")
    except Exception as e:
        print("❌ Failed to post callback:", e)
        print(json.dumps(payload))

if __name__ == "__main__":
    user, email = create_temp_email()
    register_arcgis(user, email)
    username, password = random_username(), random_password()
    post_back(username, password, email)
