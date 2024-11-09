import requests
from scraper import *
from routes import *


def main():

    # TODO : enkel URL "https://www.antwerpen.be/" meegeven en itereren over alle pagina's
    # TODO : webpagina's filteren op artikels (bv. menu pagina's niet)

    # path = "data/"

    urls = [
        'https://www.antwerpen.be/info/6425aa55d52b786c5e30501a/wist-je-dat-10-geschiedenis-weetjes-over-linkeroever',
        'https://www.antwerpen.be/info/een-studentenjob-bij-stad-antwerpen',
        'https://visit.antwerpen.be/6-verbazingwekkende-dingen-die-je-nog-niet-wist-over-antwerpen-en-het-steen',
        'https://www.antwerpen.be/nl/overzicht/sporting-a/wandelen/acht-voordelen-van-wandelen'
    ]
    print("Starting Scraper...")
    for index, url in enumerate(urls):
        lines = scrape(url)
        response = post_data({"url": url, "text": lines})

        # Check the response
        if response.status_code == 200:
            print(f"{index + 1} out of {len(urls)} successfully completed ({url})")
        else:
            print(f"{index + 1} out of {len(urls)} failed, status code: {response.status_code} ({url})")
    print("Stopping Scraper...")


if __name__ == '__main__':
    main()
    close_driver()
