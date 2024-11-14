from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

from enums import Framework
from text_manipulation import remove_html_tags, filter_html, clean_html
import os

# Chrome: headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Selenium WebDriver
service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
# service = Service(executable_path='/opt/homebrew/bin/chromedriver')

driver = webdriver.Chrome(service=service, options=chrome_options)


def close_driver():
    """Close the Selenium WebDriver."""
    driver.quit()


def scrape(url):
    """Scrape the specified URL and return cleaned text."""
    filtered_elements = ""
    driver.get(url)
    time.sleep(1)
    page_source = driver.page_source

    # PARSE
    soup = BeautifulSoup(page_source, 'html.parser')

    # FILTER OUT TEXT
    soup = remove_html_tags(soup, 'div', 'm-image__copyright a-copyright')

    # FILTER TEXT
    framework = detect_framework()

    match framework:
        case Framework.ANGULAR:
            filtered_elements = filter_html(soup, 'div', 'article-container', 1)
        case Framework.REACT | Framework.UNKNOWN:
            filtered_elements = filter_html(soup, 'div', 'u-container', 2)

    # CLEAN TEXT
    cleaned_lines = []
    for element in filtered_elements:
        # Instead of passing the list, extract text directly
        cleaned_lines.extend(clean_html(element))  # Pass each element individually
    return cleaned_lines  # Return the cleaned lines instead of the last processed variable


def detect_framework():
    """Use Selenium to execute JavaScript in the console to detect Angular or React."""
    # Check for Angular
    is_angular = driver.execute_script("return (window.angular !== undefined)")
    if is_angular:
        return Framework.ANGULAR

    # Check for React
    is_react = driver.execute_script("return (window.React !== undefined || window.ReactDOM !== undefined)")
    if is_react:
        return Framework.REACT

    # Return unknown if no framework is detected
    return Framework.UNKNOWN
