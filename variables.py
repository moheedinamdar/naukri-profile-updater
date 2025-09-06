# Chrome options
CHROME_OPTIONS = {
    'start_maximized': '--start-maximized',
    'disable_dev_shm': '--disable-dev-shm-usage',
    'no_sandbox': '--no-sandbox',
    'disable_gpu': '--disable-gpu',
    'user_agent': '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'headless': '--headless=new'  # New headless mode for Chrome
}

# Browser settings
RUN_HEADLESS = True  # Set to False to see the browser window

# URLs
NAUKRI_LOGIN_URL = 'https://www.naukri.com/nlogin/login'
NAUKRI_PROFILE_URL = 'https://www.naukri.com/mnjuser/profile'

# WebDriver wait time (in seconds)
WEBDRIVER_WAIT_TIME = 30
LOGIN_WAIT_TIME = 5
PAGE_LOAD_WAIT_TIME = 5
ANIMATION_WAIT_TIME = 2
INPUT_WAIT_TIME = 1

# XPath Selectors
SELECTORS = {
    'username_field': "//input[@id='usernameField']",
    'password_field': "//input[@id='passwordField']",
    'login_button': "//button[@type='submit']",
    'headline_section': "//div[contains(@class, 'resumeHeadline')]",
    'headline_edit_button': "//div[contains(@class, 'resumeHeadline')]//span[contains(@class, 'edit')]",
    'headline_textarea': "//div[contains(@class, 'ltCont')]//textarea",
    'headline_dialog': "//div[contains(@class, 'ltCont')]",
    'save_button': "//button[normalize-space()='Save']",
    'save_button_alt': "//button[contains(text(), 'Save')]"
}

# Resume Headline
RESUME_HEADLINE = """Senior DevOps Engineer | DevSecOps Expert with 6+ Years in AWS, Kubernetes, CI/CD Pipelines, Security Scanning & Automation | Driving Secure, Efficient Deployments"""

# Logging Format
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'
