import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:3001"

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_01_unauthenticated_redirects_to_signin(driver):
    driver.get(BASE_URL)
    time.sleep(1)
    assert "signin" in driver.current_url or "login" in driver.current_url

def test_02_signin_page_loads(driver):
    driver.get(f"{BASE_URL}/signin")
    assert "<html" in driver.page_source.lower()

def test_03_signin_has_email_field(driver):
    driver.get(f"{BASE_URL}/signin")
    assert driver.find_element(By.CSS_SELECTOR, "input[type='email']")

def test_04_signin_has_password_field(driver):
    driver.get(f"{BASE_URL}/signin")
    assert driver.find_element(By.CSS_SELECTOR, "input[type='password']")

def test_05_signin_has_submit_button(driver):
    driver.get(f"{BASE_URL}/signin")
    assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

def test_06_signup_page_loads(driver):
    driver.get(f"{BASE_URL}/signup")
    assert "signup" in driver.current_url

def test_07_signup_has_name_field(driver):
    driver.get(f"{BASE_URL}/signup")
    assert driver.find_element(By.CSS_SELECTOR, "input[type='text']")

def test_08_signup_has_email_field(driver):
    driver.get(f"{BASE_URL}/signup")
    assert driver.find_element(By.CSS_SELECTOR, "input[type='email']")

def test_09_signup_has_password_field(driver):
    driver.get(f"{BASE_URL}/signup")
    assert driver.find_element(By.CSS_SELECTOR, "input[type='password']")

def test_10_signup_has_submit_button(driver):
    driver.get(f"{BASE_URL}/signup")
    assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

def test_11_signin_email_typing(driver):
    driver.get(f"{BASE_URL}/signin")
    field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    field.send_keys("testuser@example.com")
    assert field.get_attribute("value") == "testuser@example.com"

def test_12_signin_password_typing(driver):
    driver.get(f"{BASE_URL}/signin")
    field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    field.send_keys("Test@1234")
    assert field.get_attribute("value") == "Test@1234"

def test_13_signup_email_typing(driver):
    driver.get(f"{BASE_URL}/signup")
    field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    field.send_keys("newuser@example.com")
    assert field.get_attribute("value") == "newuser@example.com"

def test_14_signup_password_typing(driver):
    driver.get(f"{BASE_URL}/signup")
    field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    field.send_keys("SecurePass1!")
    assert field.get_attribute("value") == "SecurePass1!"

def test_15_signup_name_typing(driver):
    driver.get(f"{BASE_URL}/signup")
    field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    field.send_keys("Amna")
    assert field.get_attribute("value") == "Amna"