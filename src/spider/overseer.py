import peewee as pw
import logging
import threading

from models import database, UrlStatusModel, RequestStatusModel
from spider import Spider, Worker

class Overseer:
    def __init__(self, database):
        self.database = database
        self.spiders = list()
        self.url_status = self.load_url_status()
        self.request_status = self.load_request_status()
        logging.debug('Created Overseer')
    
    def create_spider(self):
        worker = Worker(database)
        spider = Spider(worker)
        self.spiders.append(spider)
        return spider
    
    def start_spider(self, spider, url):
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