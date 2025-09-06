import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def take_screenshot(driver, filename):
    driver.save_screenshot(f"screenshots/{filename}")
    print(f"Screenshot saved: {filename}")

def setup_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def test_login():
    driver = setup_driver()
    try:
        # Test with Google first
        driver.get('https://www.google.com')
        take_screenshot(driver, "google_test.png")
        print(f"Page title: {driver.title}")
        
        # Now try Naukri
        driver.get('https://www.naukri.com')
        take_screenshot(driver, "naukri_home.png")
        
        # Try login page
        driver.get('https://www.naukri.com/nlogin/login')
        take_screenshot(driver, "naukri_login.png")
        
        # Enter credentials
        email = os.environ.get('NAUKRI_EMAIL')
        password = os.environ.get('NAUKRI_PASSWORD')
        
        if email and password:
            print("Attempting login with provided credentials")
            email_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            password_field = driver.find_element(By.ID, "passwordField")
            password_field.clear()
            password_field.send_keys(password)
            
            take_screenshot(driver, "credentials_entered.png")
            
            # Click login
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login
            time.sleep(10)
            take_screenshot(driver, "after_login.png")
            
            # Check if we're logged in
            current_url = driver.current_url
            print(f"Current URL after login: {current_url}")
            
            # Try to access profile
            driver.get('https://www.naukri.com/mnjuser/profile')
            time.sleep(10)
            take_screenshot(driver, "profile_page.png")
            
            # Check for headline section
            try:
                headline = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'resumeHeadline')]"))
                )
                print("Resume headline section found!")
                take_screenshot(driver, "headline_found.png")
            except Exception as e:
                print(f"Could not find resume headline section: {str(e)}")
        else:
            print("No credentials provided")
        
        return True
    except Exception as e:
        print(f"Error in test_login: {str(e)}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()
