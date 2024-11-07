from scraper import scrape, close_driver
from file_operations import *
from text_manipulation import *


def main():

    # TODO : enkel URL "https://www.antwerpen.be/" meegeven en itereren over alle pagina's
    # TODO : webpagina's filteren op artikels (bv. menu pagina's niet)

    path = "data/"
    urls = [
        'https://www.antwerpen.be/info/6425aa55d52b786c5e30501a/wist-je-dat-10-geschiedenis-weetjes-over-linkeroever',
        'https://www.antwerpen.be/info/een-studentenjob-bij-stad-antwerpen',
        'https://visit.antwerpen.be/6-verbazingwekkende-dingen-die-je-nog-niet-wist-over-antwerpen-en-het-steen',
        'https://www.antwerpen.be/nl/overzicht/sporting-a/wandelen/acht-voordelen-van-wandelen'
    ]

    for index, url in enumerate(urls):
        lines = scrape(url)
        save_txt_as_file(lines, path + file_name_from_url(url))
        print("Done(%s/%s)" % (index, len(urls)))


if __name__ == '__main__':
    main()
    close_driver()
