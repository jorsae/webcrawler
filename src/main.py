import signal
from models import *
from spider import Worker, Overseer, Helper
import logging
import os

from commander import Commander

from utility import UrlStatus, RequestStatus
import arguments

def main():
    setup_logging()
    # setup_exit_handler()
    
    args = arguments.parse_arguments()
    overseer = Overseer(database)
    arguments.run_arguments(args, overseer)
    
    create_tables()
    fill_url_status_model()
    fill_request_status_model()
    Helper() #initialize the url_status & request_status lists
    
    Commander(overseer).cmdloop()
    
    # l = logging.getLogger()
    # print(l.level)
    # l.level = logging.CRITICAL
    # print(l.level)
    # test_overseer()
    # test_worker()
    # test()

def test():
    import requests
    import processor
    r = requests.get('https://realpython.com/beautiful-soup-web-scraper-python/')
    # emails = processor.url.get_emails('as', r.text)
    # print(emails)
    visible_text = processor.data.get_visible_data(r.text)
    print(visible_text)

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
    for request_status in RequestStatus:
        RequestStatusModel.get_or_create(request_status=request_status.name)
    logging.debug(f'Created {len(RequestStatus)} RequestStatus objects in db')

def fill_url_status_model():
    for url_status in UrlStatus:
        UrlStatusModel.get_or_create(url_status=url_status.name)
    logging.debug(f'Created {len(UrlStatus)} UrlStatus objects in db')

def create_tables():
    models = BaseModel.__subclasses__()
    database.create_tables(models)
    logging.debug(f'Created {len(models)} tables')

def setup_exit_handler():
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

def exit_handler(a, e):
    print('application ending')

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