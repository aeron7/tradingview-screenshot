from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
import re

def capture_tradingview_screenshot(ticker='NONE', headless=True, window_size="1280,720"):
    # Login to TradingView
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--force-dark-mode')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f"--window-size={window_size}")
    
    # Add clipboard permissions
    prefs = {
        "profile.content_settings.exceptions.clipboard": {
            "[*.]tradingview.com,*": {"setting": 1}
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized.")
    except WebDriverException as e:
        print(f"Failed to initialize WebDriver: {e}")
        return None

    # https://www.tradingview.com/chart/LuDjaV3K/
    url = "https://in.tradingview.com/chart/LuDjaV3K/?symbol=" + str(ticker)
    
    clipboard = None
    try:
        # Navigate to the URL
        print(f"Navigating to {url}")
        driver.get(url)

        # Wait for a few seconds for the new page to load
        time.sleep(5)

        print('Attempting to trigger screenshot and copy link...')
        ActionChains(driver).key_down(Keys.ALT).send_keys('s').key_up(Keys.ALT).perform()

        # Wait for the copy action to complete and clipboard to populate
        time.sleep(3)

        print("Attempting to read clipboard via JavaScript...")
        # Read clipboard using JavaScript execution
        clipboard = driver.execute_script("return navigator.clipboard.readText();")
        print(f'Clipboard content via JS: {"[empty]" if not clipboard else "[content received]"}')

        if not clipboard:
            print("Clipboard was empty. Retrying Alt+S and read...")
            # Optional: Retry logic if clipboard is empty
            ActionChains(driver).key_down(Keys.ALT).send_keys('s').key_up(Keys.ALT).perform()
            time.sleep(3)
            clipboard = driver.execute_script("return navigator.clipboard.readText();")
            print(f'Clipboard content after retry: {"[empty]" if not clipboard else "[content received]"}')

    except WebDriverException as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        if driver:
            print("Quitting browser...")
            quit_browser(driver)

    return clipboard

def quit_browser(driver):
    try:
        driver.quit()
        print("Browser quit successfully.")
    except WebDriverException as e:
        print(f"Error quitting WebDriver: {e}")

# Example usage:
clipboard_data = capture_tradingview_screenshot("BYBIT:BTCUSDT.P", headless=True)
# https://in.tradingview.com/chart/LuDjaV3K/?symbol=NSE:APOLLOTYRE

def convert_tradingview_links(input_string):
    # Define a regex pattern to find links of the format 'https://www.tradingview.com/x/...'
    pattern = r'https://www\.tradingview\.com/x/([a-zA-Z0-9]+)/'

    # Find all matching links in the input string
    matches = re.findall(pattern, input_string)

    # Iterate through the matches and replace them
    for match in matches:
        old_link = f'https://www.tradingview.com/x/{match}/'
        new_link = f'https://s3.tradingview.com/snapshots/{match[0].lower()}/{match}.png'
        input_string = input_string.replace(old_link, new_link)

    return input_string

clipboard_data = convert_tradingview_links("Chart Link: " + str(clipboard_data))
print(clipboard_data)
