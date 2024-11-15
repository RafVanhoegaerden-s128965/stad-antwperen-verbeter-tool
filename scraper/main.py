from scraper import *
from routes import *


def main():

    # Crawl over the domain to find all the urls

    print("[    Starting Crawl    ]")
    domain = "https://www.antwerpen.be"
    urls = crawl(domain)
    print("[    Stopping Crawl    ]")

    for index, url in enumerate(urls):
        # Scrape each url to get all the content
        lines = scrape(url)

        # Send data to the API
        response = post_data({"url": url, "text": lines})

        # Check API for a response code
        if response.status_code == 200:
            print(f"[{index + 1} out of {len(urls)} successfully completed]")
        else:
            print(f"[{index + 1} out of {len(urls)} failed, status code: {response.status_code}]")
    close_driver()


if __name__ == '__main__':
    print("[    Starting Scraper    ]")
    main()
    print("[    Stopping Scraper    ]")
