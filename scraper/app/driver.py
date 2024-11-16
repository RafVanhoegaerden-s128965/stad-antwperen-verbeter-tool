from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import os

_driver_instance = None


def get_driver():
    """Initialize and return a shared Selenium WebDriver instance."""
    global _driver_instance
    if _driver_instance is None:  # Create the driver only if it doesn't exist
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
        _driver_instance = webdriver.Chrome(service=service, options=chrome_options)
    return _driver_instance


def close_driver():
    """Close the shared Selenium WebDriver instance."""
    global _driver_instance
    if _driver_instance is not None:
        _driver_instance.quit()
        _driver_instance = None
