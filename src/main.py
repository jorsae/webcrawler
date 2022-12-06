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
    
    from commander import Commander
    Commander().cmdloop()
    
    # l = logging.getLogger()
    # print(l.level)
    # l.level = logging.CRITICAL
    # print(l.level)
    # test_overseer()
    # test_worker()

def test_overseer():
    overseer = Overseer(database)

    spider = overseer.create_spider()
    overseer.start_spider(spider.id, 'https://vg.no')
    # overseer.start_spider(spider.id, 'https://jorsae.github.io/CatGameCalculator/')
    # overseer.start_spider(spider.id)

    overseer.run()

def test_worker():
    worker = Worker(database)
    # worker.crawl('https://vg.no')
    worker.crawl('https://jorsae.github.io/CatGameCalculator/about.html')

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
    print_handler = logging.StreamHandler()
    logging.basicConfig(handlers=[handler], level=logging.DEBUG, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')

if __name__ == "__main__":
    main()