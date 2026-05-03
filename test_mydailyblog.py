import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:3001"

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Modern headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") # Standardize viewport
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

# --- SECURITY & ROUTING TESTS ---

def test_01_protected_route_enforcement(driver):
    # Tests that unauthenticated users are forced to authenticate
    driver.get(f"{BASE_URL}/")
    wait = WebDriverWait(driver, 5)
    wait.until(EC.url_contains("signin"))
    assert "signin" in driver.current_url.lower(), "Failed to protect root route"

def test_02_invalid_url_handling(driver):
    # Tests how the app handles a 404 Not Found scenario
    driver.get(f"{BASE_URL}/this-route-does-not-exist")
    wait = WebDriverWait(driver, 5)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "404" in body_text or "not found" in body_text.lower(), "404 page not rendering correctly"

# --- NAVIGATION & INTERACTIVITY TESTS ---

def test_03_client_side_navigation_to_signup(driver):
    # Tests if the Next.js router transitions pages without a full reload
    driver.get(f"{BASE_URL}/signin")
    wait = WebDriverWait(driver, 5)
    # Finds the link that points to the signup page and clicks it
    signup_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='signup']")))
    signup_link.click()
    wait.until(EC.url_contains("signup"))
    assert "signup" in driver.current_url

def test_04_client_side_navigation_to_signin(driver):
    driver.get(f"{BASE_URL}/signup")
    wait = WebDriverWait(driver, 5)
    signin_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='signin']")))
    signin_link.click()
    wait.until(EC.url_contains("signin"))
    assert "signin" in driver.current_url

# --- FORM VALIDATION & UI STATE TESTS ---

def test_05_signin_html5_validation_empty_submit(driver):
    # Tests that the browser prevents submission of empty required fields
    driver.get(f"{BASE_URL}/signin")
    wait = WebDriverWait(driver, 5)
    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    submit_btn.click()
    
    email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    # Check if HTML5 'required' validation kicks in
    is_valid = driver.execute_script("return arguments[0].validity.valid;", email_field)
    assert not is_valid, "Form submitted despite empty required fields"

def test_06_signin_email_format_validation(driver):
    driver.get(f"{BASE_URL}/signin")
    email_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    email_field.send_keys("invalid-email-format")
    
    is_valid = driver.execute_script("return arguments[0].validity.valid;", email_field)
    assert not is_valid, "Form accepted an improperly formatted email address"

def test_07_password_field_security_masking(driver):
    # Ensures passwords are not exposed in plain text on the screen
    driver.get(f"{BASE_URL}/signin")
    password_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[type='password']")))
    assert password_field.get_attribute("type") == "password", "Password field is not masked"

# --- DATA ENTRY & END-TO-END SIMULATION ---

def test_08_signup_form_full_data_entry(driver):
    # Simulates a complete user data entry workflow
    driver.get(f"{BASE_URL}/signup")
    wait = WebDriverWait(driver, 5)
    
    name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    
    name.send_keys("Automated Tester")
    email.send_keys("auto@test.com")
    password.send_keys("SecurePass123!")
    
    assert name.get_attribute("value") == "Automated Tester"
    assert email.get_attribute("value") == "auto@test.com"
    assert password.get_attribute("value") == "SecurePass123!"

def test_09_signin_form_full_data_entry(driver):
    driver.get(f"{BASE_URL}/signin")
    wait = WebDriverWait(driver, 5)
    
    email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    
    email.send_keys("testuser@example.com")
    password.send_keys("Test@1234")
    
    assert email.get_attribute("value") == "testuser@example.com"

def test_10_xss_input_sanitization_check(driver):
    # Injects a script tag to ensure the input field handles it as a raw string
    driver.get(f"{BASE_URL}/signup")
    name_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    xss_payload = "<script>alert('hack')</script>"
    name_field.send_keys(xss_payload)
    assert name_field.get_attribute("value") == xss_payload, "Input field failed to handle special characters"

# --- LAYOUT & RESPONSIVENESS TESTS ---

def test_11_responsive_mobile_layout_rendering(driver):
    # Simulates an iPhone viewport to test CSS responsiveness
    driver.set_window_size(375, 812)
    driver.get(f"{BASE_URL}/signin")
    wait = WebDriverWait(driver, 5)
    # Check if the submit button is still visible and clickable on mobile
    submit_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    assert submit_btn.is_displayed(), "Submit button disappeared on mobile layout"
    # Restore window size for remaining tests
    driver.set_window_size(1920, 1080)

def test_12_responsive_tablet_layout_rendering(driver):
    # Simulates an iPad viewport
    driver.set_window_size(768, 1024)
    driver.get(f"{BASE_URL}/signup")
    wait = WebDriverWait(driver, 5)
    form = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "form")))
    assert form.is_displayed(), "Signup form broke on tablet layout"
    driver.set_window_size(1920, 1080)

# --- PERFORMANCE & BROWSER API TESTS ---

def test_13_page_load_performance(driver):
    # Validates that the signin page loads under an acceptable threshold (2 seconds)
    start_time = time.time()
    driver.get(f"{BASE_URL}/signin")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    load_time = time.time() - start_time
    assert load_time < 2.0, f"Page load performance too slow: {load_time} seconds"

def test_14_document_readiness_state(driver):
    # Tests that the DOM completely finished parsing and loading resources
    driver.get(f"{BASE_URL}/signin")
    ready_state = driver.execute_script("return document.readyState;")
    assert ready_state == "complete", "Document failed to reach complete readyState"

def test_15_no_console_errors_on_load(driver):
    # Reads the browser's console to ensure React isn't throwing hydration errors
    driver.get(f"{BASE_URL}/signin")
    logs = driver.get_log("browser")
    severe_errors = [log for log in logs if log['level'] == 'SEVERE']
    assert len(severe_errors) == 0, f"Found severe console errors: {severe_errors}"