from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import re

def capture_tradingview_screenshot(ticker='NONE'):
    # Login to TradingView
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--force-dark-mode')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=894,579")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    url = "https://in.tradingview.com/chart/NRGn9VUO/?symbol=" + str(ticker)
    
    # Navigate to the URL
    driver.get(url)

    # Wait for a few seconds for the new page to load
    time.sleep(3)
  
    print('Chart is ready for capture')
    ActionChains(driver).key_down(Keys.ALT).key_down('s').key_up(Keys.ALT).key_up('s').perform()
    time.sleep(10)
    
    # Use xclip to get the clipboard content
    clipboard = subprocess.check_output(['xclip', '-o']).decode('utf-8')     
    
    time.sleep(5)    
        
    quit_browser(driver)

    return clipboard

def quit_browser(driver):
    driver.quit()

# Example usage:
clipboard_data = capture_tradingview_screenshot("NSE:APOLLOTYRE")
print(clipboard_data)

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
