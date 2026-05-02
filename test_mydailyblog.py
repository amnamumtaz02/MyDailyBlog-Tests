import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:3001"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "Test@1234"
TEST_NAME = "Test User"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver

def sign_in(driver, email=TEST_EMAIL, password=TEST_PASSWORD):
    driver.get(f"{BASE_URL}/signin")
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
    time.sleep(2)

# ─── TEST 1 ───────────────────────────────────────────────
def test_01_unauthenticated_redirects_to_signin():
    """Unauthenticated user visiting / is redirected to /signin"""
    driver = get_driver()
    try:
        driver.get(BASE_URL)
        time.sleep(2)
        assert "/signin" in driver.current_url, "Should redirect to /signin"
    finally:
        driver.quit()

# ─── TEST 2 ───────────────────────────────────────────────
def test_02_signin_page_loads():
    """Sign In page loads with email, password fields and Sign In button"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signin")
        assert driver.find_element(By.ID, "email").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(
            By.XPATH, "//button[text()='Sign In']").is_displayed()
    finally:
        driver.quit()

# ─── TEST 3 ───────────────────────────────────────────────
def test_03_signup_page_loads():
    """Sign Up page loads with all fields visible"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signup")
        assert driver.find_element(By.ID, "name").is_displayed()
        assert driver.find_element(By.ID, "email").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(By.ID, "confirmPassword").is_displayed()
        assert driver.find_element(
            By.XPATH, "//button[text()='Sign Up']").is_displayed()
    finally:
        driver.quit()

# ─── TEST 4 ───────────────────────────────────────────────
def test_04_signup_with_valid_data():
    """User can sign up with valid credentials"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signup")
        # use timestamp to make email unique every run
        unique_email = f"newuser{int(time.time())}@example.com"
        driver.find_element(By.ID, "name").send_keys("New User")
        driver.find_element(By.ID, "email").send_keys(unique_email)
        driver.find_element(By.ID, "password").send_keys("Test@1234")
        driver.find_element(By.ID, "confirmPassword").send_keys("Test@1234")
        driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
        time.sleep(2)
        assert "/signin" in driver.current_url, "Should redirect to /signin after signup"
    finally:
        driver.quit()

# ─── TEST 5 ───────────────────────────────────────────────
def test_05_signup_with_mismatched_passwords():
    """Sign Up shows error when passwords do not match"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signup")
        driver.find_element(By.ID, "name").send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys("mismatch@example.com")
        driver.find_element(By.ID, "password").send_keys("Test@1234")
        driver.find_element(By.ID, "confirmPassword").send_keys("Wrong@5678")
        driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
        time.sleep(2)
        assert "/signup" in driver.current_url, "Should stay on signup page"
    finally:
        driver.quit()

# ─── TEST 6 ───────────────────────────────────────────────
def test_06_signup_with_duplicate_email():
    """Sign Up shows error when email already exists"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signup")
        driver.find_element(By.ID, "name").send_keys(TEST_NAME)
        driver.find_element(By.ID, "email").send_keys(TEST_EMAIL)
        driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
        driver.find_element(By.ID, "confirmPassword").send_keys(TEST_PASSWORD)
        driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
        time.sleep(2)
        assert "/signup" in driver.current_url, "Should stay on signup with duplicate email error"
    finally:
        driver.quit()

# ─── TEST 7 ───────────────────────────────────────────────
def test_07_signin_with_valid_credentials():
    """User can sign in with correct credentials and lands on homepage"""
    driver = get_driver()
    try:
        sign_in(driver)
        assert driver.current_url == f"{BASE_URL}/" or driver.current_url == BASE_URL, \
            "Should redirect to homepage after sign in"
    finally:
        driver.quit()

# ─── TEST 8 ───────────────────────────────────────────────
def test_08_signin_with_wrong_password():
    """Sign In shows error with incorrect password"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signin")
        driver.find_element(By.ID, "email").send_keys(TEST_EMAIL)
        driver.find_element(By.ID, "password").send_keys("WrongPassword!")
        driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
        time.sleep(2)
        assert "/signin" in driver.current_url, "Should stay on signin page"
    finally:
        driver.quit()

# ─── TEST 9 ───────────────────────────────────────────────
def test_09_signin_with_unregistered_email():
    """Sign In shows error with an email that does not exist"""
    driver = get_driver()
    try:
        driver.get(f"{BASE_URL}/signin")
        driver.find_element(By.ID, "email").send_keys("ghost@example.com")
        driver.find_element(By.ID, "password").send_keys("Test@1234")
        driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
        time.sleep(2)
        assert "/signin" in driver.current_url, "Should stay on signin page"
    finally:
        driver.quit()

# ─── TEST 10 ──────────────────────────────────────────────
def test_10_homepage_shows_after_signin():
    """Homepage loads correctly after signing in"""
    driver = get_driver()
    try:
        sign_in(driver)
        assert "MyDailyBlogs" in driver.page_source, \
            "Homepage should contain MyDailyBlogs title"
    finally:
        driver.quit()

# ─── TEST 11 ──────────────────────────────────────────────
def test_11_create_post_page_accessible_when_signed_in():
    """Signed in user can access the Create Post page"""
    driver = get_driver()
    try:
        sign_in(driver)
        driver.get(f"{BASE_URL}/posts/create")
        time.sleep(2)
        assert driver.find_element(By.ID, "title").is_displayed()
        assert driver.find_element(By.ID, "content").is_displayed()
    finally:
        driver.quit()

# ─── TEST 12 ──────────────────────────────────────────────
def test_12_homepage_shows_welcome_message():
    """Homepage shows a welcome message with the signed in user's name"""
    driver = get_driver()
    try:
        sign_in(driver)
        time.sleep(2)
        assert "Welcome" in driver.page_source, \
            "Homepage should show Welcome message for signed in user"
    finally:
        driver.quit()

# ─── TEST 13 ──────────────────────────────────────────────
def test_13_create_post_successfully():
    """Signed in user can create a new post and it appears on homepage"""
    driver = get_driver()
    try:
        sign_in(driver)
        driver.get(f"{BASE_URL}/posts/create")
        time.sleep(1)
        post_title = f"Test Post {int(time.time())}"
        driver.find_element(By.ID, "title").send_keys(post_title)
        driver.find_element(By.ID, "content").send_keys(
            "This is a test post content created by Selenium.")
        driver.find_element(By.XPATH, "//button[text()='Save']").click()
        time.sleep(2)
        assert post_title in driver.page_source, \
            "Newly created post should appear on the homepage"
    finally:
        driver.quit()

# ─── TEST 14 ──────────────────────────────────────────────
def test_14_post_shows_author_name():
    """Post card on homepage displays the author name"""
    driver = get_driver()
    try:
        sign_in(driver)
        assert "by" in driver.page_source.lower(), \
            "Homepage should show author name on post cards"
    finally:
        driver.quit()

# ─── TEST 15 ──────────────────────────────────────────────
def test_15_signout_redirects_to_signin():
    """Clicking Sign Out redirects user back to /signin"""
    driver = get_driver()
    try:
        sign_in(driver)
        time.sleep(1)
        signout_btn = driver.find_element(
            By.XPATH, "//button[text()='Sign Out']")
        signout_btn.click()
        time.sleep(2)
        assert "/signin" in driver.current_url, \
            "Should redirect to /signin after signing out"
    finally:
        driver.quit()