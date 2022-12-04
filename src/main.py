import peewee as pw
from models import *
from spider import Worker, Overseer
import logging
import os

import utility

def main():
    setup_logging()

    create_tables()
    fill_url_status_model()
    fill_request_status_model()
    
    test_overseer()
    # test_worker()

def test_overseer():
    overseer = Overseer(database)
    print(overseer.url_status)
    print(overseer.request_status)

    spider = overseer.create_spider()
    print(spider)
    overseer.start_spider(spider, 'https://jorsae.github.io/CatGameCalculator/')

    print(spider.thread)

def test_worker():
    worker = Worker(database)
    worker.crawl('https://jorsae.github.io/CatGameCalculator/')
    worker.crawl('https://vg.no')

def fill_request_status_model():
    for request_status in utility.RequestStatus.RequestStatus:
        RequestStatusModel.get_or_create(request_status=request_status.name)
    logging.debug(f'Created {len(utility.RequestStatus.RequestStatus)} RequestStatus objects in db')

def fill_url_status_model():
    for url_status in utility.UrlStatus.UrlStatus:
        UrlStatusModel.get_or_create(url_status=url_status.name)
    logging.debug(f'Created {len(utility.UrlStatus.UrlStatus)} UrlStatus objects in db')

def create_tables():
    models = BaseModel.__subclasses__()
    database.create_tables(models)
    logging.debug(f'Created {len(models)} tables')

def setup_logging():
    logFolder = './logs'
    logFile = 'webcrawler.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    handler = logging.FileHandler(filename=f'{logFolder}/{logFile}', encoding='utf-8', mode='a+')
    logging.basicConfig(handlers=[handler], level=logging.DEBUG, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')

if __name__ == "__main__":
    main()