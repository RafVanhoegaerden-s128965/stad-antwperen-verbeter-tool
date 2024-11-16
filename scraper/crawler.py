from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from driver import *


def crawl(base_url, whitelist):
    """
    Continuously crawl pages starting from the base URL,
    only visiting URLs that match the whitelist.
    """
    driver = get_driver()
    to_crawl = [base_url]  # Queue of URLs to crawl
    crawled = set()        # Set of already visited URLs
    valid_urls = []  # List to store unique crawling results

    excluded_extensions = (
        ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", "#main"
    )

    excluded_terms = (
        "tel:", "mailto:", "assets-proxy", "feature1", "icon", "img",
        "javascript:", "/api", "/srv", "cookiebeleid"
    )

    def is_valid_url(unvalidated_url):
        """
        Check if a URL is valid based on whitelist, excluded extensions, and terms.
        """
        return (
                any(unvalidated_url.startswith(allowed) for allowed in whitelist)  # Whitelist check
                and not unvalidated_url.endswith(excluded_extensions)  # Excluded extensions
                and not any(term in unvalidated_url for term in excluded_terms)  # Excluded terms
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
            valid_urls.append(current_url)  # Save the visited URL

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

    return valid_urls
