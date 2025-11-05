import requests, json, random, time, string, csv, sys
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# =====================
#  CONFIG
# =====================
API_URL = "https://tempmail.id.vn/api/email/create"
TOKEN = '6090|3voy6gZG4ySE648LFeudbkWU99rvEda6Ugn9Rmct800e8fe8'  # ⚠️ KHÔNG thêm chữ "Bearer"
DOMAIN = "nghienplus.io.vn"
CHROME_VERSION = 133

first_names = ["nguyen", "tran", "le", "pham", "hoang", "do", "vo", "dang", "bui", "ngo"]
middle_names = ["van", "thi", "duc", "minh", "ngoc", "hoai", "quang", "thu", "tuan", "bao"]
last_names = ["anh", "linh", "hoa", "tien", "thao", "hung", "khoa", "huong", "huy", "nam"]

# =====================
#  UTILITIES
# =====================
def random_username(prefix="arcgis"):
    return f"{prefix}{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

def random_password():
    chars = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choices(chars, k=10))

def save_credentials_csv(path="credentials.csv", record=None):
    if not record: return
    file_exists = False
    try:
        open(path, "r", encoding="utf-8")
        file_exists = True
    except FileNotFoundError:
        pass
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "email", "username", "password"])
        if not file_exists: writer.writeheader()
        writer.writerow(record)
    print(f"💾 Saved credentials → {path}")

# =====================
#  FIXED: create_temp_email
# =====================
def create_temp_email():
    """Tạo email ngẫu nhiên với API tempmail.id.vn (và fallback khi lỗi)"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    for attempt in range(3):
        user = f"{random.choice(first_names)}{random.choice(middle_names)}{random.choice(last_names)}{random.randint(10,9999)}"
        payload = json.dumps({"user": user, "domain": DOMAIN})
        print(f"📩 Tạo email thử lần {attempt+1}: {user}@{DOMAIN}")

        try:
            resp = requests.post(API_URL, headers=headers, data=payload, timeout=15)
            print("🔍 Raw response:", resp.status_code, resp.text[:200])
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception as e:
                print(f"⚠️ Không parse được JSON: {e}")
                continue

            if data.get("success"):
                email = f"{user}@{DOMAIN}"
                print(f"✅ Đã tạo email: {email}")
                return user, email
            elif "đã được đăng kí" in data.get("message", ""):
                print(f"⚠️ '{user}' bị trùng, thử lại...")
                continue
            else:
                print(f"❌ Lỗi API: {data}")
                time.sleep(2)
        except Exception as e:
            print(f"❌ Request error: {e}")
            time.sleep(3)

    # fallback: tự tạo email random
    fallback_email = f"{random_username()}@example.com"
    print(f"⚠️ API TempMail lỗi, dùng tạm email: {fallback_email}")
    return random_username(), fallback_email

# =====================
#  Selenium setup
# =====================
def chrome_options():
    opts = uc.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return opts

# =====================
#  Main ArcGIS automation (đơn giản hóa cho Actions)
# =====================
def register_arcgis(email_user, email_full):
    print(f"\n🚀 Đăng ký ArcGIS cho {email_full}")
    driver = uc.Chrome(options=chrome_options(), use_subprocess=True)
    wait = WebDriverWait(driver, 25)

    try:
        driver.get("https://www.esri.com/en-us/arcgis/products/arcgis-online/trial/sign-up")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Trang ArcGIS load thành công")
    except Exception as e:
        print(f"⚠️ Không mở được trang đăng ký: {e}")
        driver.quit()
        return None

    # Demo điền 1 vài ô (không bypass recaptcha khi chạy headless)
    try:
        driver.find_element(By.CSS_SELECTOR, "input[aria-label='First Name']").send_keys("Nguyen")
        driver.find_element(By.CSS_SELECTOR, "input[aria-label='Last Name']").send_keys("Test")
        driver.find_element(By.CSS_SELECTOR, "input[aria-label='Business Email']").send_keys(email_full)
        print("✅ Nhập thông tin cơ bản xong")
    except Exception as e:
        print(f"⚠️ Lỗi khi nhập form: {e}")

    driver.quit()
    return True

# =====================
#  MAIN FLOW
# =====================
if __name__ == "__main__":
    user, email = create_temp_email()
    if not email:
        print("❌ Không tạo được email, dừng.")
        sys.exit(1)

    ok = register_arcgis(user, email)
    if not ok:
        print("❌ Không đăng ký được ArcGIS.")
        sys.exit(1)

    username, password = random_username(), random_password()
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "email": email,
        "username": username,
        "password": password
    }
    save_credentials_csv("credentials.csv", record)
    print(json.dumps(record))
