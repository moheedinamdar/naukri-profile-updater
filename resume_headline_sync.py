try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: undetected_chromedriver not available: {e}")
    UC_AVAILABLE = False
    
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementNotInteractableException,
    TimeoutException
)
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

try:
    from fake_useragent import UserAgent
    from random_user_agent.user_agent import UserAgent as RandomUA
    from random_user_agent.params import SoftwareName, OperatingSystem
    USER_AGENT_AVAILABLE = True
except ImportError:
    print("Warning: User agent libraries not available, using fallback")
    USER_AGENT_AVAILABLE = False

from dotenv import load_dotenv
import os
import time
import random
from datetime import datetime
import logging
from variables import (
    CHROME_OPTIONS, NAUKRI_LOGIN_URL, NAUKRI_PROFILE_URL,
    WEBDRIVER_WAIT_TIME, LOGIN_WAIT_TIME, PAGE_LOAD_WAIT_TIME,
    ANIMATION_WAIT_TIME, INPUT_WAIT_TIME, SELECTORS,
    RESUME_HEADLINE, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    RUN_HEADLESS
)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

def create_sample_env_file():
    """Create a sample .env file for local development"""
    sample_content = """# Naukri Profile Updater Environment Variables
# Copy this file and rename it to .env, then fill in your actual credentials

NAUKRI_EMAIL=your-email@example.com
NAUKRI_PASSWORD=your-password-here

# Note: Never commit the actual .env file to version control
# The .env file should be listed in .gitignore
"""
    
    try:
        with open('.env.sample', 'w') as f:
            f.write(sample_content)
        logger.info("Created .env.sample file as a template")
        logger.info("Copy .env.sample to .env and fill in your actual credentials")
    except Exception as e:
        logger.warning(f"Could not create .env.sample file: {e}")

def load_credentials():
    """Load Naukri login credentials from environment variables or .env file"""
    
    # Check if running in CI environment
    is_ci = os.getenv('CI', 'false').lower() == 'true'
    
    # First try to load from environment variables directly (works for both CI and local)
    email = os.getenv('NAUKRI_EMAIL')
    password = os.getenv('NAUKRI_PASSWORD')
    
    if email and password:
        logger.info("Credentials loaded from environment variables")
        return email, password
    
    # If not in CI and credentials not found in environment, check for .env file
    if not is_ci:
        env_file_path = '.env'
        if os.path.exists(env_file_path):
            logger.info(f"Found .env file at {env_file_path}, loading credentials")
            load_dotenv(env_file_path)
            email = os.getenv('NAUKRI_EMAIL')
            password = os.getenv('NAUKRI_PASSWORD')
            
            if email and password:
                logger.info("Credentials loaded successfully from .env file")
                return email, password
            else:
                logger.warning("Found .env file but credentials are missing or empty")
        else:
            logger.info("No .env file found in current directory")
            # Create a sample .env file to help the user
            create_sample_env_file()
    
    # If we reach here, credentials were not found
    if is_ci:
        logger.error("Running in CI environment but required secrets (NAUKRI_EMAIL, NAUKRI_PASSWORD) are not set")
        raise ValueError("Please configure NAUKRI_EMAIL and NAUKRI_PASSWORD secrets in GitHub repository settings")
    else:
        logger.error("Credentials not found in environment variables or .env file")
        logger.info("To fix this, either:")
        logger.info("1. Create a .env file with NAUKRI_EMAIL and NAUKRI_PASSWORD")
        logger.info("2. Set environment variables: export NAUKRI_EMAIL='...' && export NAUKRI_PASSWORD='...'")
        raise ValueError("Please set NAUKRI_EMAIL and NAUKRI_PASSWORD in environment variables or .env file")

def update_resume_headline():
    """Update the resume headline on Naukri profile"""
    logger.info("=== Starting Naukri Resume Headline Update ===")
    
    # Log the headline that will be used
    logger.info(f"Resume headline to be set: {RESUME_HEADLINE}")
    
    # Setup Chrome options with anti-bot measures
    logger.info("Configuring Chrome browser options with anti-bot measures")
    
    # Check if running in CI environment
    is_ci = os.getenv('CI', 'false').lower() == 'true'
    
    # Check availability of undetected chrome for this session
    uc_available_local = UC_AVAILABLE
    
    if is_ci:
        logger.info("Running in CI environment - using optimized settings")
        # In CI, use regular selenium with enhanced anti-bot measures        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--lang=en-US')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        
        # Enhanced anti-bot options for CI
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Add more realistic browser profile settings
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 1
            },
            "profile.default_content_settings": {
                "popups": 0
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        logger.info("Initializing Chrome browser for CI environment")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Enhanced anti-bot scripts for CI
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        })
        
        # Set additional properties to look more human
        driver.execute_script("""
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        """)
        
        # Visit Google first to build session history
        logger.info("Building session history...")
        driver.get('https://www.google.com')
        time.sleep(random.uniform(2, 4))
        
        # Search for something to make it look more natural
        try:
            search_box = driver.find_element(By.NAME, 'q')
            search_box.send_keys('naukri jobs')
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(3, 5))
        except:
            pass  # Ignore if search fails
        
    else:
        logger.info("Running in local environment")
        
        # Generate random user agent for local development
        if USER_AGENT_AVAILABLE:
            try:
                software_names = [SoftwareName.CHROME.value]
                operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
                user_agent_rotator = RandomUA(software_names=software_names, operating_systems=operating_systems, limit=100)
                random_user_agent = user_agent_rotator.get_random_user_agent()
            except:
                # Fallback user agent if random generation fails
                random_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        else:
            random_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        
        # Try undetected Chrome first if available
        if uc_available_local:
            logger.info("Using undetected Chrome for local environment")
            try:
                # Configure undetected-chromedriver for local use
                options = uc.ChromeOptions()
                options.add_argument(f'--user-agent={random_user_agent}')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-extensions')
                options.add_argument('--no-sandbox')
                options.add_argument('--dns-prefetch-disable')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-infobars')
                options.add_argument('--lang=en-US')
                options.add_argument('--disable-dev-shm-usage')
                
                # Disable password saving prompt
                prefs = {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 2
                }
                options.add_experimental_option("prefs", prefs)
                
                # Random window size to avoid detection
                widths = [1920, 1366, 1536, 1440, 1280]
                heights = [1080, 768, 864, 900, 720]
                random_width = random.choice(widths)
                random_height = random.choice(heights)
                options.add_argument(f'--window-size={random_width},{random_height}')
                
                if RUN_HEADLESS:
                    logger.info("Running in headless mode")
                    options.add_argument('--headless')
                else:
                    logger.info("Running in visible mode (not headless)")
                
                # Get Chrome major version
                chrome_version = 139  # Set to your current Chrome version
                driver = uc.Chrome(options=options, version_main=chrome_version)  # Use specific version
                logger.info("Successfully initialized undetected Chrome")
                
            except Exception as e:
                logger.warning(f"Failed to initialize undetected Chrome: {e}")
                uc_available_local = False  # Mark as unavailable for this session
        
        # Fallback to regular Chrome if undetected is not available
        if not uc_available_local:
            logger.info("Using regular Chrome with enhanced anti-bot measures")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f'--user-agent={random_user_agent}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable password saving prompt
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            if RUN_HEADLESS:
                chrome_options.add_argument('--headless')
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Add anti-bot scripts for regular Chrome
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    # Set random delay for wait time to mimic human behavior
    base_wait = WEBDRIVER_WAIT_TIME
    random_wait = base_wait + random.uniform(1, 5)
    wait = WebDriverWait(driver, random_wait)
    
    # Modify navigator.webdriver flag if not already done
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except:
        pass  # Ignore if already executed
    
    # Add random delays between actions
    time.sleep(random.uniform(1, 3))
    
    logger.info("Chrome browser initialized successfully with anti-bot measures")
    
    try:
        # Load credentials and login
        email, password = load_credentials()
        driver.get(NAUKRI_LOGIN_URL)
        
        # Login with human-like behavior
        def human_type(element, text):
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random delay between keystrokes
                
        def safe_click(element, driver):
            """Safely click an element with fallback methods"""
            try:
                # Scroll element into view first
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.5)
                
                # Try direct click first
                element.click()
                time.sleep(random.uniform(0.3, 0.8))
                logger.info("Direct click successful")
                
            except Exception as e:
                logger.info(f"Direct click failed: {e}, trying alternative methods")
                try:
                    # Try JavaScript click
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(random.uniform(0.3, 0.8))
                    logger.info("JavaScript click successful")
                    
                except Exception as e2:
                    logger.info(f"JavaScript click failed: {e2}, trying ActionChains")
                    try:
                        # Try ActionChains with safer movement
                        actions = ActionChains(driver)
                        actions.move_to_element(element).click().perform()
                        time.sleep(random.uniform(0.3, 0.8))
                        logger.info("ActionChains click successful")
                        
                    except Exception as e3:
                        logger.error(f"All click methods failed: {e3}")
                        raise e3
            
        # Simulate human-like login behavior with improved error handling
        logger.info("Starting login process with human-like behavior")
        
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['username_field'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['username_field'])))
        wait.until(EC.visibility_of(username_field))
        
        # Safely click and enter username
        safe_click(username_field, driver)
        username_field.clear()
        time.sleep(random.uniform(0.3, 0.8))
        human_type(username_field, email)
        logger.info("Username entered successfully")
        
        # Random delay before moving to password
        time.sleep(random.uniform(0.8, 1.5))
        
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['password_field'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['password_field'])))
        wait.until(EC.visibility_of(password_field))
        
        # Safely click and enter password
        safe_click(password_field, driver)
        password_field.clear()
        time.sleep(random.uniform(0.3, 0.8))
        human_type(password_field, password)
        logger.info("Password entered successfully")
        
        # Random delay before clicking login
        time.sleep(random.uniform(1.0, 2.0))
        
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['login_button'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['login_button'])))
        wait.until(EC.visibility_of(login_button))
        
        # Safely click login button
        safe_click(login_button, driver)
        logger.info("Login button clicked successfully")
        
        # Add random delay after login attempt
        time.sleep(random.uniform(2.0, 4.0))
        
        # Check for CAPTCHA or other challenges
        logger.info("Checking for CAPTCHA or login challenges...")
        
        # Wait a bit longer to see what happens after login
        time.sleep(5)
        
        # Check for various CAPTCHA types and challenges
        captcha_detected = False
        captcha_selectors = [
            "//div[contains(@class, 'captcha')]",
            "//div[contains(@class, 'recaptcha')]", 
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(text(), 'verify')]",
            "//div[contains(text(), 'robot')]",
            "//div[contains(text(), 'human')]",
            "//div[contains(text(), 'security')]",
            "//div[contains(text(), 'challenge')]",
            "//canvas[@id='captchaCanvas']",
            "//img[contains(@alt, 'captcha')]",
            "//div[@id='challenge']",
            "//form[contains(@class, 'captcha')]"
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = driver.find_element(By.XPATH, selector)
                if captcha_element.is_displayed():
                    captcha_detected = True
                    logger.warning(f"CAPTCHA detected with selector: {selector}")
                    break
            except:
                continue
        
        # Additional checks for login failure indicators
        login_error_selectors = [
            "//div[contains(text(), 'Invalid')]",
            "//div[contains(text(), 'incorrect')]",
            "//div[contains(text(), 'failed')]",
            "//div[contains(@class, 'error')]",
            "//span[contains(@class, 'error')]"
        ]
        
        login_error = False
        for selector in login_error_selectors:
            try:
                error_element = driver.find_element(By.XPATH, selector)
                if error_element.is_displayed():
                    login_error = True
                    logger.warning(f"Login error detected: {error_element.text}")
                    break
            except:
                continue
        
        if captcha_detected:
            logger.warning("CAPTCHA challenge detected - implementing workarounds...")
            
            # Strategy 1: Wait for manual resolution in non-CI environments
            if not is_ci:
                logger.info("Running locally - waiting for manual CAPTCHA resolution...")
                logger.info("Please solve the CAPTCHA manually in the browser window")
                
                # Wait up to 2 minutes for CAPTCHA to be resolved
                captcha_timeout = 120
                start_time = time.time()
                
                while time.time() - start_time < captcha_timeout:
                    try:
                        # Check if we've moved past the login page
                        current_url = driver.current_url
                        if 'login' not in current_url.lower():
                            logger.info("CAPTCHA appears to be resolved - continuing...")
                            break
                        
                        # Check if CAPTCHA is still visible
                        captcha_still_present = False
                        for selector in captcha_selectors:
                            try:
                                captcha_element = driver.find_element(By.XPATH, selector)
                                if captcha_element.is_displayed():
                                    captcha_still_present = True
                                    break
                            except:
                                continue
                        
                        if not captcha_still_present:
                            logger.info("CAPTCHA no longer detected - continuing...")
                            break
                            
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.debug(f"Error during CAPTCHA wait: {e}")
                        time.sleep(2)
                
                if time.time() - start_time >= captcha_timeout:
                    logger.error("CAPTCHA resolution timeout - manual intervention required")
                    
            else:
                # Strategy 2: In CI, try alternative approaches
                logger.warning("CAPTCHA detected in CI environment - trying alternative strategies...")
                
                # Try refreshing and retrying with different timing
                time.sleep(random.uniform(3, 7))
                
                # Check if we can proceed anyway
                try:
                    # Sometimes the login succeeds despite CAPTCHA appearance
                    driver.get(NAUKRI_PROFILE_URL)
                    time.sleep(5)
                    
                    # Check if we can access profile page
                    try:
                        profile_indicator = wait.until(
                            EC.presence_of_element_located((By.XPATH, SELECTORS['headline_section'])), 
                            timeout=10
                        )
                        logger.info("Successfully bypassed CAPTCHA - profile page accessible")
                    except TimeoutException:
                        logger.error("CAPTCHA blocking access - profile page not accessible")
                        # Take screenshot for debugging
                        try:
                            driver.save_screenshot("screenshots/captcha_blocked.png")
                            logger.info("Screenshot saved: captcha_blocked.png")
                        except:
                            pass
                        raise Exception("CAPTCHA challenge cannot be resolved in CI environment")
                        
                except Exception as e:
                    logger.error(f"Failed to bypass CAPTCHA: {e}")
                    raise
        
        elif login_error:
            logger.error("Login failed due to credentials or other error")
            raise Exception("Login failed - check credentials")
        
        else:
            logger.info("No CAPTCHA detected - proceeding with normal flow")
        
        # Wait for login to complete and verify
        time.sleep(LOGIN_WAIT_TIME)
        try:
            wait.until(lambda driver: driver.current_url != NAUKRI_LOGIN_URL)
            logger.info("Login successful - URL changed")
        except TimeoutException:
            logger.warning("Login may not have completed - URL didn't change")
        
        # Navigate to profile page
        logger.info("Navigating to Naukri profile page")
        driver.get(NAUKRI_PROFILE_URL)
        
        # Wait for profile page to load and ensure we're logged in
        time.sleep(PAGE_LOAD_WAIT_TIME)
        logger.info("Checking login status")
        
        try:
            # Wait for either headline section or login button
            headline_or_login = wait.until(
                EC.presence_of_element_located((By.XPATH, 
                    f"{SELECTORS['headline_section']} | //button[contains(text(), 'Login')]")))
            
            # Handle login if needed
            if "Login" in headline_or_login.text:
                logger.info("Login required - proceeding with login")
                wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['username_field']))).send_keys(email)
                wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['password_field']))).send_keys(password)
                wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['login_button']))).click()
                time.sleep(LOGIN_WAIT_TIME)
                driver.get(NAUKRI_PROFILE_URL)
                time.sleep(PAGE_LOAD_WAIT_TIME)
                
                # Re-check for headline section after login
                headline_or_login = wait.until(
                    EC.presence_of_element_located((By.XPATH, SELECTORS['headline_section'])))
            
            logger.info("Successfully located headline section")
        except TimeoutException as e:
            logger.error("Could not locate headline section")
            raise Exception("Failed to access profile page") from e
        
        # Locate and update headline
        logger.info("Proceeding with resume headline update")
        
        # Scroll headline section into view and wait for it to be stable
        try:
            headline_section = wait.until(EC.presence_of_element_located(
                (By.XPATH, SELECTORS['headline_section'])))
            driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -100);", headline_section)
            time.sleep(ANIMATION_WAIT_TIME)
            logger.info("Found and scrolled to resume headline section")
        except TimeoutException as e:
            logger.error("Failed to locate resume headline section")
            raise Exception("Could not find resume headline section on profile page") from e        # Find and click edit button with enhanced error handling
        try:
            headline_edit = wait.until(EC.presence_of_element_located(
                (By.XPATH, SELECTORS['headline_edit_button'])))
            wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['headline_edit_button'])))
            wait.until(EC.visibility_of(headline_edit))
            
            # Ensure the element is in view and not covered
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", headline_edit)
            time.sleep(ANIMATION_WAIT_TIME)
            
            try:
                # Try direct click
                headline_edit.click()
            except (ElementNotInteractableException, StaleElementReferenceException):
                logger.info("Direct click failed, trying JavaScript click")
                try:
                    driver.execute_script("arguments[0].click();", headline_edit)
                except:
                    logger.info("JavaScript click failed, trying Actions chain")
                    actions = ActionChains(driver)
                    actions.move_to_element(headline_edit).click().perform()
            
            logger.info("Successfully clicked edit headline button")
            time.sleep(ANIMATION_WAIT_TIME * 2)  # Extra wait for animation
            
        except TimeoutException as e:
            logger.error(f"Could not find or click edit button: {str(e)}")
            raise
            
        # Update headline text with enhanced error handling
        try:
            # Wait for textarea with multiple conditions
            headline_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, SELECTORS['headline_textarea'])))
            wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['headline_textarea'])))
            wait.until(EC.visibility_of(headline_input))
            
            # Ensure the element is in view and not covered
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", headline_input)
            time.sleep(ANIMATION_WAIT_TIME)
            
            # Clear existing text with retry mechanism
            retry_count = 3
            for attempt in range(retry_count):
                try:
                    logger.info(f"Attempt {attempt + 1} to clear existing headline text")
                    headline_input.click()  # Ensure focus
                    time.sleep(INPUT_WAIT_TIME)
                    headline_input.clear()
                    # Verify clear worked
                    if not headline_input.get_attribute('value'):
                        logger.info("Successfully cleared headline text")
                        break
                except (ElementNotInteractableException, StaleElementReferenceException) as e:
                    if attempt == retry_count - 1:
                        raise e
                    logger.warning(f"Clear attempt {attempt + 1} failed, retrying...")
                    time.sleep(INPUT_WAIT_TIME)
            
            # Enter new headline with retry mechanism
            for attempt in range(retry_count):
                try:
                    logger.info(f"Attempt {attempt + 1} to enter new headline")
                    headline_input.click()  # Ensure focus
                    time.sleep(INPUT_WAIT_TIME)
                    
                    # Clear and verify it's cleared
                    headline_input.clear()
                    if headline_input.get_attribute('value'):
                        logger.warning("Textarea not cleared, trying alternative clear method")
                        headline_input.send_keys(Keys.CONTROL + "a")  # Select all
                        headline_input.send_keys(Keys.DELETE)         # Delete selection
                    
                    # Enter new headline
                    headline_input.send_keys(RESUME_HEADLINE)
                    current_value = headline_input.get_attribute('value')
                    logger.info(f"Current textarea value: {current_value}")
                    
                    # Verify text was entered
                    if current_value == RESUME_HEADLINE:
                        logger.info("Successfully entered new headline")
                        break
                except (ElementNotInteractableException, StaleElementReferenceException) as e:
                    if attempt == retry_count - 1:
                        raise e
                    logger.warning(f"Text entry attempt {attempt + 1} failed, retrying...")
                    time.sleep(INPUT_WAIT_TIME)
            
            # Ensure focus is moved away from the input
            headline_input.send_keys(Keys.TAB)
            time.sleep(INPUT_WAIT_TIME * 2)  # Extra wait for any auto-save
            
        except Exception as e:
            logger.error(f"Error updating headline text: {str(e)}")
            raise
            
        # Save changes
        logger.info("Looking for Save button")
        time.sleep(ANIMATION_WAIT_TIME)
        
        try:
            # Find save button
            save_button = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['save_button'])))
            wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['save_button'])))
            wait.until(EC.visibility_of(save_button))
            logger.info("Found Save button")
            
            # Ensure button is in view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
            time.sleep(ANIMATION_WAIT_TIME)
            
            # Click save button once and exit immediately
            save_button.click()
            logger.info("Save button clicked")
            
            # Exit immediately after clicking save
            success_message = f"Update completed at {datetime.now()}"
            print(success_message)
            logger.info(success_message)
            logger.info("Closing browser...")
            driver.quit()
            logger.info("Browser closed successfully")
            logger.info("=== Resume headline update completed ===\n")
            return  # Exit function immediately after successful save
            
        except Exception as e:
            logger.error(f"Save failed: {str(e)}")
            raise  # Re-raise the exception to be handled by the outer try-except
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise
        
    finally:
        try:
            logger.info("Attempting to close browser")
            driver.close()  # Close the current window
            time.sleep(1)   # Give it a moment
            driver.quit()   # Quit the driver completely
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            try:
                # Force quit if normal close failed
                driver.quit()
                logger.info("Browser force quit successful")
            except:
                logger.error("Failed to force quit browser")
        finally:
            logger.info("=== Resume headline update completed ===\n")

if __name__ == "__main__":
    update_resume_headline()
