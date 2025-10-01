"""
This code is used to automate signing in and extracting necessary
authorization for getting ESPN Fantasy League data via API
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class ESPNFantasyExtractor:
    """
    This class is used to extract fantasy league data via api.
    """
    def __init__(self, headless: bool=False):
        self.driver = None
        self.espn_s2 = None
        self.swid = None
        self.setup_driver(headless)

    def setup_driver(self, headless=False):
        """
        Setup Chrome Driver for automation of login
        """
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        if headless:
            chrome_options.add_argument("--headless")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Driver setup failed: {e}")
            raise

    def login_and_wait(self, username: str, password: str, manual_login: bool=False):
        """
        This should automate the login process unless the user sets manual_login to true.
        """
        try:
            print("Navigating to ESPN fantasy page...")
            self.driver.get('https://www.espn.com/fantasy')
            try: 
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                    '[data-testid="profile-management"]'))
                )
                print("Already logged in!")
                return True
            except TimeoutException:
                print("Not logged in, proceeding with login...")
            
            login_selectors = [
                '[data-testid="login-button"]',
                'a[href*="login"]'
                '.user-not-authenticated a',
                '.login-cta'
            ]
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue

            if login_button:
                login_button.click()
                print("Clicked login button")
                time.sleep(2)
            else:
                self.driver.get('https://www.espn.com/login')
                print("Navigated to login page directly")

            if manual_login:
                print("\n" + "="*50)
                print("MANUAL LOGIN MODE")
                print("="*50)
                print("Please complete the login process in the browser window.")
                print("This includes:")
                print("- Entering your username/password")
                print("- Completing any CAPTCHA")
                print("- Handling 2FA if enabled")
                print("- Accepting any terms/conditions")
                print("\nOnce you're logged in and can see ESPN Fantasy content,")
                input("press Enter to continue...")
                return True
            
            wait = WebDriverWait(self.driver, 15)

            try:
                iframe = wait.until(EC.presence_of_element_located((By.NAME, "disneyid-iframe")))
                self.driver.switch_to.frame(iframe)
                print("Switched to Disney ID frame")
            except TimeoutException:
                print("No iframe detected")

            username_selectors = [
                'input[placeholder*="Username"]',
                'input[placeholder*="Email"]',
                'input[type="email"]',
                'input[name="email"]'
            ]

            username_field = None
            for selector in username_selectors:
                try:
                    username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue

            if username_field:
                username_field.clear()
                username_field.send_keys(username)
                print("Username entered")
            else:
                print("Could not find username field")
                print("Switching to manual mode...")
                input("Please complete login manually and press Enter...")
                self.driver.switch_to.default_content()
                return True
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.clear()
            password_field.send_keys(password)
            print("Password entered")


            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            print("Login submitted")

            self.driver.switch_to.default_content()

            time.sleep(5)

            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()

            if any(challenge in page_source for challenge in ['captcha', 'verify', '2fa', 'two-factor']):
                print(" Additional verification required")
                input("Please complete verification and press Enter when done...")

            elif 'login' in current_url:
                print("Still on login page - may need manual intervention")
                input("Please complete login manually if needed and press Enter...")

            self.driver.get('https://www.espn.com/fantasy')
            time.sleep(3)

            return True

        except Exception as e:
            print(f"Login error: {e}")
            print("Please complete login manually...")
            input("Press Enter when login is complete...")
            return True

def main():
    """
    This is the main function to extract the fantasy league info.
    """
    username = input("Enter your ESPN username or email address: ")
    password = input("Enter your ESPN password: ")

    driver = webdriver.Chrome()
    driver.get('https://www.espn.com/login')
    WebDriverWait(driver, 10)
    driver.find_element(By.CSS_SELECTOR,
        'input[placeholder*="Username"], input[placeholder*="Email"]').send_keys(username)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    WebDriverWait(driver, 10)
    print("Success in automation!")

# cookies = driver.get_cookies()