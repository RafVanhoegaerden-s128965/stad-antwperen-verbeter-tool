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


def crawl(base_url, whitelist):
    """
    Continuously crawl pages starting from the base URL,
    only visiting URLs that match the whitelist.
    """
    to_crawl = [base_url]  # Queue of URLs to crawl
    crawled = set()        # Set of already visited URLs
    all_article_urls = []  # List to store unique crawling results

    excluded_extensions = (
        ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", "#main"
    )

    excluded_terms = (
        "tel:", "mailto:", "assets-proxy", "feature1", "icon", "img",
        "javascript:", "/api", "/srv", "cookiebeleid"
    )

    def is_valid_url(url):
        """
        Check if a URL is valid based on whitelist, excluded extensions, and terms.
        """
        return (
            any(url.startswith(allowed) for allowed in whitelist)  # Whitelist check
            and not url.endswith(excluded_extensions)  # Excluded extensions
            and not any(term in url for term in excluded_terms)  # Excluded terms
        )

    while to_crawl:
        current_url = to_crawl.pop(0)  # Get the next URL from the queue
        if current_url in crawled:
            continue  # Skip if already visited

        # Skip URLs not in the whitelist
        if not is_valid_url(current_url):
            print(f"Skipped (not in whitelist): {current_url}")
            continue

        print(f"Crawling: {current_url}")
        try:
            driver.get(current_url)
            crawled.add(current_url)  # Mark this URL as visited
            all_article_urls.append(current_url)  # Save the visited URL

            # Wait for JavaScript-loaded content
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "a")) > 0
                )
            except TimeoutException:
                print("No new content loaded.")
                continue

            # Collect all visible links after JS execution
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if href:
                        # Handle relative URLs
                        if href.startswith("/"):
                            href = base_url + href

                        # Check validity before adding to the queue
                        if href not in crawled and href not in to_crawl and is_valid_url(href):
                            to_crawl.append(href)  # Add new URLs to crawl queue
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue

            # Capture URLs from network requests
            for request in driver.requests:
                try:
                    if request.response:
                        url = request.url
                        if url.startswith("/"):  # Handle relative URLs
                            url = base_url + url
                        if url not in crawled and url not in to_crawl and is_valid_url(url):
                            to_crawl.append(url)  # Add new URLs to crawl queue
                except Exception as e:
                    print(f"Error processing network request: {e}")
                    continue

            print(f"Current to_crawl queue: {to_crawl}")
            print(f"Visited URLs: {crawled}")

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            continue

    return all_article_urls


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
