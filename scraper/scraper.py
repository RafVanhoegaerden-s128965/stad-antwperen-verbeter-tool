import os
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from seleniumwire import webdriver
from text_manipulation import remove_html_tags, filter_html, clean_html
from enums import Framework

# Chrome: headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Selenium WebDriver
service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
driver = webdriver.Chrome(service=service, options=chrome_options)


def close_driver():
    """Close the Selenium WebDriver."""
    driver.quit()


def crawl(base_url):
    """Capture sub-URLs dynamically loaded by JavaScript on the page."""
    driver.get(base_url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )
    except TimeoutException:
        print("Page load timeout")
        return []

    # Print all <a> tags found after the wait
    all_links = driver.find_elements(By.TAG_NAME, "a")
    article_urls = set()
    excluded_extensions = (
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg"
    )

    excluded_terms = (
        "tel:",
        "mailto:",
        "assets-proxy",
        "feature1",
        "icon",
        "img",
        "javascript:void(0);"
    )

    for link in all_links:
        href = link.get_attribute("href")
        if href:
            # Filter out unwanted links based on the file extensions and terms
            if not href.endswith(excluded_extensions) and not any(term in href for term in excluded_terms):
                article_urls.add(href)
                print(f"Kept: {href}")
            else:
                print(f"Filtered out: {href}")

    # Ensure we capture network requests via Selenium Wire
    print("Waiting for network requests to be captured...")
    # Increase the wait time to allow all requests to finish
    WebDriverWait(driver, 5).until(lambda driver: len(driver.requests) > 0)

    # Capture URLs from network requests
    print("Capturing network requests:")
    for request in driver.requests:
        if request.response:
            url = request.url
            print(f"Request URL: {url}")

            # Check if URL is relative or matches base_url
            if url.startswith(base_url) or url.startswith("/"):
                # Handle relative URLs by prepending the base URL
                if url.startswith("/"):
                    url = base_url + url

                # Filter out URLs with excluded extensions and terms
                if not url.endswith(excluded_extensions) and not any(term in url for term in excluded_terms):
                    article_urls.add(url)
                    print(f"Kept: {url}")
                else:
                    print(f"Filtered out: {url}")
            else:
                print(f"Ignored: {url}")

    return list(article_urls)


def scrape(url):
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
    """Use Selenium to execute JavaScript in the console to detect Angular or React."""
    is_angular = driver.execute_script("return (window.angular !== undefined)")
    if is_angular:
        return Framework.ANGULAR

    is_react = driver.execute_script("return (window.React !== undefined || window.ReactDOM !== undefined)")
    if is_react:
        return Framework.REACT

    return Framework.UNKNOWN
