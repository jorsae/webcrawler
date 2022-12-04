import peewee as pw
import logging
import time
import threading

import constants
from models import *
from spider import Spider, Worker

class Overseer:
    def __init__(self, database):
        self.database = database
        self.spiders = list()
        self.url_status = self.load_url_status()
        self.request_status = self.load_request_status()
        logging.debug('Created Overseer')
    
    def run(self):
        while True:
            for spider in self.spiders:
                if not spider.thread.is_alive():
                    spider.thread.handled = True
                    self.restart_spider(spider)
            time.sleep(1)
    
    def restart_spider(self, spider):
        print(f'{spider.worker.domain[0]=}')
        print(f'{spider.worker.domain=}')
        if len(spider.worker.queue) <= 0:
            urls = (CrawlQueueModel.select(CrawlQueueModel.url)
                    .where(CrawlQueueModel.domain_id == spider.worker.domain[0])
                    .limit(constants.MAXIMUM_URLS_IN_WORKER_QUEUE)
                    )
            for url in urls:
                print(f'{url.url=}')
                spider.worker.queue.add(url.url)
            self.start_spider(spider)

    def create_spider(self):
        worker = Worker(database)
        spider = Spider(worker)
        self.spiders.append(spider)
        return spider
    
    def start_spider(self, spider, url=None):
        spider.thread = threading.Thread(target=spider.worker.crawl, args=(url, ))
        spider.thread.start()
        logging.info(f'Starting spider with: {url}')
    
    def load_url_status(self):
        url_status = [url_status for url_status in UrlStatusModel.select()]
        logging.debug(f'Loading {len(url_status)} url_statuses')
        return url_status
    
    def load_request_status(self):
        request_status = [request_status for request_status in RequestStatusModel.select()]
        logging.debug(f'Loading {len(request_status)} request_status')
        return request_status