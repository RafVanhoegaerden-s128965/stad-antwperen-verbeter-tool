import time
from bs4 import BeautifulSoup
from enums import Framework

from driver import *
from text_manipulation import *


def scrape(url):
    driver = get_driver()
    """Scrape the specified URL and return cleaned text."""
    driver.get(url)
    time.sleep(1)  # Allow time for the content to fully load
    page_source = driver.page_source

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    soup = remove_html_tags(soup, 'div', 'm-image__copyright a-copyright')

    framework = detect_framework()
    match framework:
        case Framework.ANGULAR:
            filtered_elements = filter_html(soup, 'div', 'article-container', 1)
        case Framework.REACT | Framework.UNKNOWN:
            filtered_elements = filter_html(soup, 'div', 'u-container', 2)

    # Clean text
    cleaned_lines = []
    for element in filtered_elements:
        cleaned_lines.extend(clean_html(element))  # Extract and clean text
    return cleaned_lines


def detect_framework():
    driver = get_driver()
    """Use Selenium to execute JavaScript in the console to detect Angular or React."""
    is_angular = driver.execute_script("return (window.angular !== undefined)")
    if is_angular:
        return Framework.ANGULAR

    is_react = driver.execute_script("return (window.React !== undefined || window.ReactDOM !== undefined)")
    if is_react:
        return Framework.REACT

    return Framework.UNKNOWN
