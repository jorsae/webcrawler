import peewee as pw
import logging
import time
import threading
import copy
from datetime import datetime

import constants
from models import *
from spider import Spider, Worker

class Overseer:
    crawl_queue = list()
    crawl_queue_lock = threading.Lock()
    @staticmethod
    def add_crawl_queue(value):
        try:
            with Overseer.crawl_queue_lock:
                Overseer.crawl_queue += value
        except Exception as e:
            logging.critical('Failed to add items to crawl_queue')

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
            
            if len(Overseer.crawl_queue) > constants.MAX_URLS_IN_CRAWL_QUEUE:
                self.add_crawl_queue_database()
            time.sleep(1)
    
    def restart_spider(self, spider):
        if len(spider.worker.queue) <= 0:
            urls = (CrawlQueueModel.select(CrawlQueueModel.url)
                    .where(CrawlQueueModel.domain_id == spider.worker.domain.domain[0])
                    .limit(constants.MAXIMUM_URLS_IN_WORKER_QUEUE)
                    )
            for url in urls:
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
    
    def add_crawl_queue_database(self):
        logging.info(f'Adding items to crawl_queue: {len(Overseer.crawl_queue)}')
        with Overseer.crawl_queue_lock:
            logging.debug(f'add_crawl_queue_database locked for deepcopy')
            crawl_queue = copy.deepcopy(Overseer.crawl_queue)
            Overseer.crawl_queue.clear()
        
        logging.debug(f'Processing crawl_queue to add to database')
        crawl_queue.sort(key=lambda x: x)
        unique_ids = list({x.domain[0].id: x for x in crawl_queue}.values())
        for unique_id in unique_ids:
            crawl_queue_processed = []
            timestamp = datetime.now()

            for url_domain in crawl_queue:
                if  url_domain.domain[0].id == unique_id.domain[0].id:
                    crawl_queue_processed.append(
                        {
                            'url': url_domain.url,
                            'priority': 0,
                            'timestamp': timestamp,
                            'domain_id': url_domain.domain[0].id
                        })
            try:
                (CrawlQueueModel
                    .insert_many(crawl_queue_processed)
                    .on_conflict(action='IGNORE')
                    .execute())
                logging.info(f'Added {len(crawl_queue_processed)} urls to crawl_queue')
            except Exception as e:
                logging.info(f'Failed to add {len(crawl_queue_processed)} urls to crawl_queue: {e}')
        logging.info('Finished adding crawl_queue to database')

    def load_url_status(self):
        url_status = [url_status for url_status in UrlStatusModel.select()]
        logging.debug(f'Loading {len(url_status)} url_statuses')
        return url_status
    
    def load_request_status(self):
        request_status = [request_status for request_status in RequestStatusModel.select()]
        logging.debug(f'Loading {len(request_status)} request_status')
        return request_status