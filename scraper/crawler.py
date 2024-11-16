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
    all_article_urls = []  # List to store unique crawling results

    excluded_extensions = (
        ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", "#main", ".htm", ".htm#"
    )

    excluded_terms = (
        "tel:", "mailto:", "assets-proxy", "feature1", "icon", "img",
        "javascript:", "/api", "/srv", "cookiebeleid"
    )

    while to_crawl:
        current_url = to_crawl.pop(0)  # Get the next URL from the queue
        if current_url in crawled:
            continue  # Skip if already visited

        # Skip URLs not in the whitelist
        if not any(current_url.startswith(allowed) for allowed in whitelist):
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

                        # Check whitelist, excluded terms, and extensions
                        if (
                            href not in crawled and href not in to_crawl
                            and any(href.startswith(allowed) for allowed in whitelist)
                            and not href.endswith(excluded_extensions)
                            and not any(term in href for term in excluded_terms)
                        ):
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
                        if (
                            url not in crawled and url not in to_crawl
                            and any(url.startswith(allowed) for allowed in whitelist)
                            and not url.endswith(excluded_extensions)
                            and not any(term in url for term in excluded_terms)
                        ):
                            to_crawl.append(url)  # Add new URLs to crawl queue
                except Exception as e:
                    print(f"Error processing network request: {e}")
                    continue

            # Limit dynamic content exploration
            dynamically_loaded_links = driver.find_elements(By.TAG_NAME, "a")
            for link in dynamically_loaded_links:
                try:
                    href = link.get_attribute("href")
                    if (
                        href and href not in crawled and href not in to_crawl
                        and any(href.startswith(allowed) for allowed in whitelist)
                        and not href.endswith(excluded_extensions)
                        and not any(term in href for term in excluded_terms)
                    ):
                        to_crawl.append(href)
                except Exception as e:
                    print(f"Error processing dynamically loaded link: {e}")
                    continue

            print(f"Current to_crawl queue: {to_crawl}")
            print(f"Visited URLs: {crawled}")

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            continue

    return all_article_urls
