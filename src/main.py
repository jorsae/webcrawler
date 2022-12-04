from models import *
from spider import Worker

import utility

def main():
    create_tables()
    fill_url_status_model()
    fill_request_status_model()
    test()

def test():
    worker = Worker(database)
    worker.crawl('https://jorsae.github.io/CatGameCalculator/')
    worker.crawl('https://vg.no')

def fill_request_status_model():
    for request_status in utility.RequestStatus.RequestStatus:
        RequestStatusModel.get_or_create(request_status=request_status.name)

def fill_url_status_model():
    for url_status in utility.UrlStatus.UrlStatus:
        UrlStatusModel.get_or_create(url_status=url_status.name)

def create_tables():
    database.create_tables([UrlStatusModel, RequestStatusModel, DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])

if __name__ == "__main__":
    main()