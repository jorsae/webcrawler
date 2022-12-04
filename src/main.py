from models import *
from spider import Spider

import utility

spider = Spider(database)

def main():
    create_tables()
    fill_url_code_model()
    test()

def test():
    spider = Spider(database)
    url = spider.get_robots_url("https://www.vg.no/robots.txt")
    print(f'robotsurl: {url}')
    res = spider.parse_robots(url)
    print(f'parse result: {res}')

    print(spider.robot_parser.can_fetch('*', 'sport/fotball/i/0QB6bM/peles-helsetilstand-forverret-faar-lindrende-behandling?utm_source=vgfront&utm_content=hovedlopet_row1_pos1&utm_medium=df-86-w24b2f3b'))
    print(spider.robot_parser.can_fetch('*', 'sport/fotball/i/0QB6bM/peles-helsetilstand-forverret-faar-lindrende-behandling?utm_source=vgfront&utm_content=hovedlopet_row1_pos1&utm_medium=df-86-w24b2f3b/tegneserier/salesposter'))
    print(spider.robot_parser.can_fetch('*', 'https://www.vg.no/poll'))
    print(spider.last_robots_domain)
    spider.crawl('https://jorsae.github.io/CatGameCalculator/')

def fill_url_code_model():
    for url_code in utility.UrlCode.UrlCode:
        UrlCodeModel.get_or_create(url_code=url_code.name)

def create_tables():
    database.create_tables([UrlCodeModel, DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])


if __name__ == "__main__":
    main()