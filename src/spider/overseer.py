import logging
import time
import threading
import copy
from datetime import datetime

import constants
from models import *
from spider import Spider, Worker
import spider

class Overseer:
    crawl_queue = list()
    crawl_queue_lock = threading.Lock()
    @staticmethod
    def add_crawl_queue(value):
        try:
            with Overseer.crawl_queue_lock:
                if type(value) == list:
                    Overseer.crawl_queue += value
                else:
                    Overseer.crawl_history.append(value)
        except Exception as e:
            logging.critical('Failed to add items to crawl_queue')

    crawl_history = list()
    crawl_history_lock = threading.Lock()
    @staticmethod
    def add_crawl_history(value):
        try:
            with Overseer.crawl_history_lock:
                if type(value) == list:
                    Overseer.crawl_history += value
                else:
                    Overseer.crawl_history.append(value)
        except Exception as e:
            logging.critical('Failed to add items to crawl_history')

    def __init__(self, database):
        self.database = database
        self.spiders = list()

        self.__spider_ids = 0
        logging.debug('Created Overseer')
    
    def run(self):
        while True:
            for spider in self.spiders:
                if spider.thread is not None:
                    if not spider.thread.is_alive():
                        spider.thread.handled = True
                        self.get_spider_urls(spider)
                        self.start_spider(spider.id)
            
            if len(Overseer.crawl_queue) >= constants.MAX_URLS_IN_CRAWL_QUEUE:
                self.add_crawl_queue_database()
            
            if len(Overseer.crawl_history) >= constants.MAX_URLS_IN_CRAWL_HISTORY:
                self.add_crawl_history_database()
            
            time.sleep(1)
    
    def get_spider_urls(self, spider):
        queue_len = len(spider.worker.queue)
        # Refill urls with same domain
        if len(spider.worker.queue) <= 0 and spider.worker.domain is not None:
            urls = (CrawlQueueModel.select(CrawlQueueModel.url)
                    .where(CrawlQueueModel.domain_id == spider.worker.domain.get_domain_id())
                    .limit(constants.MAXIMUM_URLS_IN_WORKER_QUEUE)
                    )
            for url in urls:
                spider.worker.queue.add(url.url)
        
        # Spider has no domain OR refilling previously had no more urls.
        # Get new domain for the spider
        if spider.worker.domain is None or len(spider.worker.queue) <= 0:
            domains = []
            for spider in self.spiders:
                if spider.worker.domain is not None:
                    domains.append(spider.worker.domain.get_domain_id())
            
            new_url = (CrawlQueueModel
                        .select()
                        .where(CrawlQueueModel.domain_id.not_in(domains))
                        .order_by(CrawlQueueModel.priority)
                        .limit(1)
                        )
            if len(new_url) > 0:
                spider.worker.queue.add(new_url[0].url)
            else:
                logging.debug('No urls for the spider')
        
        logging.info(f'Filled queue from: {queue_len} --> {len(spider.worker.queue)}')
    
    def create_spider(self):
        worker = Worker(database, self.__spider_ids)
        spider = Spider(worker, self.__spider_ids)
        self.spiders.append(spider)
        self.__spider_ids += 1
        return spider
    
    def start_spider(self, id, url=None):
        for spider in self.spiders:
            if spider.id == id:
                spider.thread = threading.Thread(target=spider.worker.crawl, args=(url, ))
                spider.thread.start()
        logging.info(f'Starting spider {spider.id} with: {url}')
    
    def add_crawl_queue_database(self):
        # TODO: Don't allow duplicate entries that match either CrawlHistory or CrawlQueue
        logging.debug(f'Adding items to crawl_queue: {len(Overseer.crawl_queue)}')
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
                mass_insert_query = (CrawlQueueModel
                                        .insert_many(crawl_queue_processed)
                                        .on_conflict(action='IGNORE')
                                        .as_rowcount()
                                        .execute())
                logging.debug(f'Added {mass_insert_query}/{len(crawl_queue_processed)} urls to crawl_queue')
            except Exception as e:
                logging.info(f'Failed to add {len(crawl_queue_processed)} urls to crawl_queue: {e}')
        logging.info('Finished adding crawl_queue to database')

    def add_crawl_history_database(self):
        logging.info(f'Adding items to crawl_history: {len(Overseer.crawl_history)}')
        with Overseer.crawl_history_lock:
            logging.debug(f'add_crawl_history_database locked for deepcopy')
            crawl_history = copy.deepcopy(Overseer.crawl_history)
            Overseer.crawl_history.clear()
        
        logging.debug(f'Processing crawl_history to add to database')
        crawl_history.sort(key=lambda x: x)
        unique_ids = list({x.domain[0].id: x for x in crawl_history}.values())
        for unique_id in unique_ids:
            domain_id = unique_id.domain[0].id
            crawl_history_processed = []
            timestamp = datetime.now()

            for url_domain in crawl_history:
                if  url_domain.domain[0].id == domain_id:
                    crawl_history_processed.append(
                        {
                            'url': url_domain.url,
                            'timestamp': timestamp,
                            'http_status_code': url_domain.http_status_code,
                            'request_status': spider.Helper.request_status[url_domain.request_status.name],
                            'domain_id': domain_id
                        })
            try:
                (CrawlHistoryModel
                    .insert_many(crawl_history_processed)
                    .on_conflict(action='IGNORE')
                    .execute())
                logging.info(f'Added {len(crawl_history_processed)} urls to crawl_history')
            except Exception as e:
                logging.info(f'Failed to add {len(crawl_history_processed)} urls to crawl_history: {e}')
        logging.info('Finished adding crawl_history to database')