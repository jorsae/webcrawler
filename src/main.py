from models import *
from spider import Worker

import utility

def main():
    create_tables()
    fill_url_code_model()
    test()

def test():
    worker = Worker(database)
    worker.crawl('https://jorsae.github.io/CatGameCalculator/')
    worker.crawl('https://vg.no')

def fill_url_code_model():
    for url_code in utility.UrlCode.UrlCode:
        UrlCodeModel.get_or_create(url_code=url_code.name)

def create_tables():
    database.create_tables([UrlCodeModel, DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])


if __name__ == "__main__":
    main()