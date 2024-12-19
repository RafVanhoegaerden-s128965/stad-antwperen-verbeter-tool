from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from file_operations import *
from text_manipulation import *
import time


def main():
    # Initialize Chrome WebDriver
    def initialize_driver():
        options = Options()
        # Uncomment the following lines to run in headless mode
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    # Function to handle cookie banner
    def handle_cookie_banner(driver):
        try:
            cookie_banner = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//tiktok-cookie-banner"))
            )
            print("Cookie banner found.")

            # Access the shadow root of the cookie banner
            shadow_root = driver.execute_script("return arguments[0].shadowRoot", cookie_banner)
            print("Shadow root accessed.")

            try:
                # Directly locate the button inside the shadow DOM without XPath
                allow_all_button = shadow_root.find_element(By.TAG_NAME, 'button')
                print("Cookie button found.")
                # allow_all_button.click()

            except Exception as e:
                print(f"No cookie button found: {e}")
                # Optional: If you want to try another method for targeting the button:
                allow_all_button = shadow_root.find_element(By.CSS_SELECTOR, 'button')  # Assuming there's only one button
                if allow_all_button:
                    print("Cookie button found via CSS Selector.")
                    time.sleep(3)
                    allow_all_button.click()
                    time.sleep(3)  # Allow UI to stabilize
                else:
                    print("No cookie button found via CSS Selector.")

        except Exception as e:
            print(f"No cookie banner found: {e}")

    # Function to click the refresh button
    def click_refresh_button(driver):
        try:
            refresh_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'css-tlik2g-Button-StyledButton')]"))
            )
            time.sleep(3)  # Allow UI to stabilize
            ActionChains(driver).move_to_element(refresh_button).click().perform()
            print("Refresh button clicked.")
            time.sleep(3)  # Allow UI to stabilize
        except Exception as e:
            print(f"No refresh button found or failed to click: {e}")

    # Function to scrape video descriptions
    def scrape_tiktok_descriptions(profile_url, scroll_pause_time=4):
        driver = initialize_driver()
        driver.get(profile_url)

        # Handle cookie banner
        handle_cookie_banner(driver)

        # Click the refresh button
        click_refresh_button(driver)

        # Wait for the page to load until a div with "DivItemContainerV2" in its class name is found
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'DivItemContainerV2')]")
                )
            )
            print("Page loaded: Found a div containing 'DivItemContainerV2' in its class name.")
        except Exception as e:
            print(f"Error waiting for page load: {e}")
            driver.quit()
            return []

        video_descriptions = []
        seen_descriptions = set()  # Track unique descriptions
        last_height = driver.execute_script("return document.body.scrollHeight")
        print(f"Initial page height: {last_height}")

        while True:
            # Locate video descriptions stored in the alt attribute of img tags inside picture tags
            try:
                pictures = driver.find_elements(By.TAG_NAME, 'picture')
                new_descriptions = 0  # Track if any new descriptions were found on this scroll
                for picture in pictures:
                    try:
                        img = picture.find_element(By.TAG_NAME, 'img')  # Get the <img> inside <picture>
                        alt_text = img.get_attribute('alt')  # Extract the alt attribute
                        if alt_text and alt_text not in seen_descriptions:
                            processed_text = remove_after_created_by(alt_text)
                            video_descriptions.append(processed_text)
                            seen_descriptions.add(processed_text)  # Mark this description as seen
                            new_descriptions += 1
                            print(f"Processed Description: {processed_text}")
                    except Exception as inner_e:
                        print(f"Error extracting alt from <img>: {inner_e}")
                        continue

                # If no new descriptions were found, we break out of the loop
                if new_descriptions == 0:
                    print("No new descriptions found, stopping scroll.")
                    break

            except Exception as e:
                print(f"Error locating <picture> tags: {e}")
                break

            # Scroll down and wait for content to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Optionally, you could also check for visible changes in other UI elements to verify new content
            if new_height == last_height:
                print("No more content to load, stopping scroll.")
                break
            last_height = new_height

        driver.quit()
        return video_descriptions

    # Main execution
    if __name__ == "__main__":
        tiktok_profile = "https://www.tiktok.com/@stad_antwerpen"
        descriptions = scrape_tiktok_descriptions(tiktok_profile)
        if descriptions:
            save_to_json(descriptions, "../data/tiktok_descriptions.csv")
        else:
            print("No descriptions found.")


if __name__ == '__main__':
    main()
