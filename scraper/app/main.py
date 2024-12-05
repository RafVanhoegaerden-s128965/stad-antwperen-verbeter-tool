from crawler import *
from scraper import *
from routes import *


def main():


    tiktok_data = read_file_as_txt("../data/tiktok_descriptions_raw.txt")

    for index, line in enumerate(tiktok_data):
        response = post_data({"text_type": "tiktok", "url": "https://www.tiktok.com/@stad_antwerpen", "text": line})

        # Check API for a response code
        if response.status_code == 200:
            print(f"[{index + 1} out of {len(tiktok_data)} TikTok descriptions successfully sent to database]")
        else:
            print(
                f"[{index + 1} out of {len(tiktok_data)} TikTok descriptions failed to send to database, status code: {response.status_code}]")

    domain = "https://www.antwerpen.be"
    whitelist = [
        "https://antwerpen.be",
        "https://www.antwerpen.be",
        "https://visit.antwerpen.be/",
        "https://www.visit.antwerpen.be/"
    ]

    # Crawl over the domain to find all the urls
    urls = crawl(domain, whitelist)

    for index, url in enumerate(urls):
        # Scrape each url to get all the content
        lines = scrape(url)

        # Send data to the API
        response = post_data({"text_type": "article", "url": url, "text": lines})

        # Check API for a response code
        if response.status_code == 200:
            print(f"[{index + 1} out of {len(urls)} Articles successfully sent to database]")
        else:
            print(f"[{index + 1} out of {len(urls)} Articles failed to send to database, status code: {response.status_code}]")
    close_driver()


if __name__ == '__main__':
    print("[    Starting Scraper    ]")
    main()
    print("[    Stopping Scraper    ]")
