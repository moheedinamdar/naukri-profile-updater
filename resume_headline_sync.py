import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementNotInteractableException,
    TimeoutException
)
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from random_user_agent.user_agent import UserAgent as RandomUA
from random_user_agent.params import SoftwareName, OperatingSystem
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

def load_credentials():
    """Load Naukri login credentials from environment variables or .env file"""
    # First try to load from environment variables directly
    email = os.getenv('NAUKRI_EMAIL')
    password = os.getenv('NAUKRI_PASSWORD')

    # If not found and not in CI environment, try loading from .env file
    if (not email or not password) and not os.getenv('CI'):
        logger.info("Credentials not found in environment, trying .env file")
        load_dotenv()
        email = os.getenv('NAUKRI_EMAIL')
        password = os.getenv('NAUKRI_PASSWORD')

    if not email or not password:
        logger.error("Credentials not found in environment or .env file")
        raise ValueError("Please set NAUKRI_EMAIL and NAUKRI_PASSWORD in environment variables or .env file")
    
    logger.info("Credentials loaded successfully")
    return email, password

def update_resume_headline():
    """Update the resume headline on Naukri profile"""
    logger.info("=== Starting Naukri Resume Headline Update ===")
    
    # Log the headline that will be used
    logger.info(f"Resume headline to be set: {RESUME_HEADLINE}")
    
    # Setup Chrome options with anti-bot measures
    logger.info("Configuring Chrome browser options with anti-bot measures")
    
    # Check if running in CI environment
    is_ci = os.getenv('CI', 'false').lower() == 'true'
    
    if is_ci:
        logger.info("Running in CI environment - using optimized settings")
        # In CI, use regular selenium with enhanced anti-bot measures
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
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
        
        # Additional anti-bot options for CI
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        logger.info("Initializing Chrome browser for CI environment")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Anti-bot scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        })
        
    else:
        logger.info("Running in local environment - using undetected Chrome")
        # Generate random user agent for local development
        try:
            software_names = [SoftwareName.CHROME.value]
            operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
            user_agent_rotator = RandomUA(software_names=software_names, operating_systems=operating_systems, limit=100)
            random_user_agent = user_agent_rotator.get_random_user_agent()
        except:
            # Fallback user agent if random generation fails
            random_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        
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
        
        logger.info("Initializing undetected Chrome browser")
        try:
            driver = uc.Chrome(options=options, version_main=None)  # Auto-detect version
        except Exception as e:
            logger.warning(f"Failed to initialize undetected Chrome, falling back to regular Chrome: {e}")
            # Fallback to regular Chrome if undetected fails
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f'--user-agent={random_user_agent}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            if RUN_HEADLESS:
                chrome_options.add_argument('--headless')
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
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
                time.sleep(random.uniform(0.1, 0.3))  # Random delay between keystrokes
                
        def move_and_click(element, driver):
            actions = ActionChains(driver)
            # Move to a random position first
            random_x = random.randint(-100, 100)
            random_y = random.randint(-100, 100)
            actions.move_by_offset(random_x, random_y)
            # Then move to the element
            actions.move_to_element(element)
            # Add small random offset
            actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
            actions.click()
            actions.perform()
            time.sleep(random.uniform(0.5, 1.5))
            
        # Simulate human-like login behavior
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['username_field'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['username_field'])))
        wait.until(EC.visibility_of(username_field))
        
        # Move mouse naturally and click
        move_and_click(username_field, driver)
        username_field.clear()
        time.sleep(random.uniform(0.5, 1.0))
        human_type(username_field, email)
        
        # Random delay before moving to password
        time.sleep(random.uniform(1.0, 2.0))
        
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['password_field'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['password_field'])))
        wait.until(EC.visibility_of(password_field))
        
        move_and_click(password_field, driver)
        password_field.clear()
        time.sleep(random.uniform(0.5, 1.0))
        human_type(password_field, password)
        
        # Random delay before clicking login
        time.sleep(random.uniform(1.0, 2.0))
        
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, SELECTORS['login_button'])))
        wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['login_button'])))
        wait.until(EC.visibility_of(login_button))
        
        # Move mouse naturally to login button and click
        move_and_click(login_button, driver)
        
        # Add random delay after login attempt
        time.sleep(random.uniform(2.0, 4.0))
        
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
            
        # Save changes with enhanced error handling
        logger.info("Looking for Save button")
        time.sleep(ANIMATION_WAIT_TIME * 2)  # Extra wait for any animations to complete
        
        # Try multiple save button strategies with retry mechanism
        retry_count = 3
        save_successful = False
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Save attempt {attempt + 1}")
                
                # Try primary save button first
                try:
                    save_button = wait.until(EC.presence_of_element_located(
                        (By.XPATH, SELECTORS['save_button'])))
                    wait.until(EC.element_to_be_clickable((By.XPATH, SELECTORS['save_button'])))
                    wait.until(EC.visibility_of(save_button))
                    logger.info("Found primary Save button")
                except TimeoutException:
                    # Try alternative save buttons
                    logger.info("Primary save button not found, trying alternatives")
                    save_buttons = driver.find_elements(By.XPATH, SELECTORS['save_button_alt'])
                    save_button = None
                    for btn in save_buttons:
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                save_button = btn
                                logger.info("Found alternative Save button")
                                break
                        except:
                            continue
                
                if save_button:
                    # Ensure button is in view
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                    time.sleep(ANIMATION_WAIT_TIME)
                    
                    # Try different click methods
                    click_methods = [
                        lambda: save_button.click(),
                        lambda: driver.execute_script("arguments[0].click();", save_button),
                        lambda: ActionChains(driver).move_to_element(save_button).click().perform()
                    ]
                    
                    for method in click_methods:
                        try:
                            method()
                            time.sleep(ANIMATION_WAIT_TIME)
                            # Check if dialog disappeared or success indicator appeared
                            try:
                                wait.until_not(EC.presence_of_element_located((By.XPATH, SELECTORS['headline_dialog'])))
                                save_successful = True
                                logger.info("Save confirmed successful")
                                
                                # Wait for any animations or page refreshes
                                time.sleep(ANIMATION_WAIT_TIME * 2)
                                
                                # First check for success message
                                try:
                                    success_message_xpath = "//div[text()='Success']//following-sibling::div[text()='Resume Headline has been successfully saved.']"
                                    success_element = wait.until(
                                        EC.presence_of_element_located((By.XPATH, success_message_xpath)),
                                        message="Success message not found"
                                    )
                                    
                                    if success_element.is_displayed():
                                        logger.info("Success message found on page")
                                        
                                        # Now verify the headline text on the page matches what we set
                                        try:
                                            # Get the text of the headline on the profile page
                                            headline_text_element = wait.until(
                                                EC.presence_of_element_located((By.XPATH, 
                                                f"{SELECTORS['headline_section']}//div[contains(@class, 'text')]"))
                                            )
                                            displayed_headline = headline_text_element.text.strip()
                                            logger.info(f"Current headline on page: {displayed_headline}")
                                            
                                            # Compare with what we set
                                            if RESUME_HEADLINE in displayed_headline:
                                                logger.info("Resume headline verified - text matches what we set")
                                                success_message = f"Update completed at {datetime.now()}"
                                                print(success_message)
                                                logger.info(success_message)
                                                
                                                # Close browser immediately after verification
                                                logger.info("Closing browser...")
                                                driver.quit()
                                                logger.info("Browser closed successfully")
                                                logger.info("=== Resume headline update completed ===\n")
                                                return  # Exit function after successful update
                                        except Exception as e:
                                            logger.warning(f"Could not verify headline text: {str(e)}")
                                except Exception as e:
                                    logger.warning(f"Success message check failed: {str(e)}")
                                
                                break
                            except TimeoutException:
                                continue
                        except:
                            continue
                    
                    if save_successful:
                        break
                
            except Exception as e:
                if attempt == retry_count - 1:
                    logger.error(f"All save attempts failed: {str(e)}")
                    raise
                logger.warning(f"Save attempt {attempt + 1} failed: {str(e)}, retrying...")
                time.sleep(ANIMATION_WAIT_TIME)
            
            # Remove the redundant success verification that would happen after all attempts
            if save_successful and attempt == retry_count - 1:
                logger.info("Save completed on final attempt")
                # Script will close browser in finally block
                return
        
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
