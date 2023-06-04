import copy
import logging
import threading
import time
from datetime import datetime

import psutil

import constants
import spider
from models import *
from spider import Spider, Worker


class Overseer:
    crawl_queue = list()

    @staticmethod
    def add_crawl_queue(value):
        try:
            with constants.CRAWL_QUEUE_LOCK:
                if type(value) == list:
                    Overseer.crawl_queue += value
                else:
                    Overseer.crawl_history.append(value)
        except Exception as e:
            logging.critical("Failed to add items to crawl_queue")

    crawl_history = list()

    @staticmethod
    def add_crawl_history(value):
        try:
            with constants.CRAWL_HISTORY_LOCK:
                if type(value) == list:
                    Overseer.crawl_history += value
                else:
                    Overseer.crawl_history.append(value)
        except Exception as e:
            logging.critical("Failed to add items to crawl_history")

    def __init__(self, database):
        self.database = database
        self.spiders = list()
        self.run_overseer = True

        self.__spider_ids = 0
        logging.debug("Created Overseer")

    def run(self):
        process = psutil.Process()
        index = 0
        while self.run_overseer:
            used_domains = []
            for spider in self.spiders:
                # Spider has domain
                if spider.worker.domain is not None:
                    spider_domain_id = spider.worker.domain.get_domain_id()
                    if spider_domain_id is not None:
                        used_domains.append(spider_domain_id)

            new_domain_count = 0
            for spider in self.spiders:
                # Spider is put on pause
                if spider.stop:
                    continue
                # No spider thread
                if spider.thread is None:
                    logging.error(f"No spider.thread: {spider}")
                    continue
                if spider.thread.is_alive() is False:
                    self.start_spider(spider.id)
                spider.thread.handled = True
                # Refill urls to spider if needed & possible
                self.get_spider_urls(spider)
                # Find new domain for the spider
                if spider.worker.domain is None or len(spider.worker.queue) <= 0:
                    added_new_domain = self.get_spider_domain(
                        spider, used_domains, new_domain_count
                    )
                    if added_new_domain:
                        new_domain_count += 1
                    self.start_spider(spider.id)

            if len(Overseer.crawl_queue) >= constants.MAX_URLS_IN_CRAWL_QUEUE:
                self.add_crawl_queue_database()

            if index > 10:
                mib = round(process.memory_info().rss / 1024 / 1024, 2)
                logging.debug(
                    f"CPU:{psutil.cpu_percent()}% / MEM:{psutil.virtual_memory().percent}% ({mib}MiB) | crawl_history:{len(self.crawl_history)} / crawl_queue:{len(self.crawl_queue)}"
                )
                index = 10
            index += 1
            time.sleep(constants.OVERSEER_RUN_DELAY / 1000)

    def get_spider_urls(self, spider, index=0):
        queue_len = len(spider.worker.queue)
        # Refill urls with same domain
        if (
            len(spider.worker.queue) <= constants.MIN_URLS_IN_WORKER_QUEUE
            and spider.worker.domain is not None
        ):
            urls = (
                CrawlQueueModel.select(CrawlQueueModel.url)
                .where(CrawlQueueModel.domain_id == spider.worker.domain.get_domain_id())
                .limit(constants.MAX_URLS_IN_WORKER_QUEUE)
            )
            for url in urls:
                spider.worker.queue.add(url.url)

        if len(spider.worker.queue) <= 0 and index == 0:
            logging.info("Filled queue is empty, force dumping Overseer.crawl_queue and re-trying")
            self.add_crawl_queue_database()
            self.get_spider_urls(spider, 1)
        else:
            logging.info(f"Filled queue from: {queue_len} --> {len(spider.worker.queue)}")

    def get_spider_domain(self, spider, used_domains, new_domain_count):
        new_url = (
            CrawlQueueModel.select(CrawlQueueModel.url)
            .where(CrawlQueueModel.domain_id.not_in(used_domains))
            .order_by(CrawlQueueModel.priority)
            .group_by(CrawlQueueModel.domain_id)
            .limit(new_domain_count + 1)
        )
        if len(new_url) > 0:
            spider.worker.domain = None
            spider.worker.queue.add(new_url[new_domain_count].url)
            logging.debug(f"[{spider.id}] Assigned url: {new_url[new_domain_count].url}")
            return True
        else:
            logging.debug("No urls for the spider")
            return False

    def create_spider(self):
        worker = Worker(database, self.__spider_ids)
        spider = Spider(worker, self.__spider_ids)
        self.spiders.append(spider)
        self.__spider_ids += 1
        return spider

    def start_spider(self, id, url=None):
        for spider in self.spiders:
            if spider.id == id:
                spider.thread = threading.Thread(target=spider.worker.crawl, args=(url,))
                spider.worker.run = True
                spider.stop = False
                spider.thread.start()
                logging.info(f"Starting spider {spider.id} with: {url}")
                return True
        return False

    def start_all_spiders(self):
        for spider in self.spiders:
            self.start_spider(spider.id)

    def stop_spider(self, id):
        for spider in self.spiders:
            if spider.id == id:
                spider.stop = True
                spider.stop_worker()
                spider.stop_thread()
                logging.info(f"Stopped spider: {spider.id}")

    def stop_all_spiders(self):
        # Faster to make all stop working before joining the threads
        for spider in self.spiders:
            spider.stop = True
            spider.stop_worker()

        for spider in self.spiders:
            spider.stop_thread()
            logging.info(f"Stopped spider: {spider.id}")

    def add_crawl_queue_database(self):
        logging.debug(f"Adding items to crawl_queue: {len(Overseer.crawl_queue)}")
        with constants.CRAWL_QUEUE_LOCK:
            logging.debug(f"add_crawl_queue_database locked for deepcopy")
            crawl_queue = copy.deepcopy(Overseer.crawl_queue)
            Overseer.crawl_queue.clear()

        logging.debug(f"Processing crawl_queue to add to database")
        crawl_queue.sort(key=lambda x: x)
        unique_ids = list({x.domain[0].id: x for x in crawl_queue}.values())
        for unique_id in unique_ids:
            crawl_queue_processed = []
            timestamp = datetime.now()

            for url_domain in crawl_queue:
                if url_domain.get_domain_id() == unique_id.get_domain_id():
                    if self.url_in_database(url_domain.url) is False:
                        crawl_queue_processed.append(
                            {
                                "url": url_domain.url,
                                "priority": 0,
                                "timestamp": timestamp,
                                "domain_id": url_domain.get_domain_id(),
                            }
                        )
            try:
                mass_insert_query = (
                    CrawlQueueModel.insert_many(crawl_queue_processed)
                    .on_conflict(action="IGNORE")
                    .as_rowcount()
                    .execute()
                )
                logging.debug(
                    f"Added {mass_insert_query}/{len(crawl_queue_processed)} urls to crawl_queue"
                )
            except Exception as e:
                logging.error(
                    f"Failed to add {len(crawl_queue_processed)} urls to crawl_queue: {e}"
                )
        logging.info("Finished adding crawl_queue to database")

    def url_in_database(self, url):
        try:
            cq = CrawlQueueModel.select().where(CrawlQueueModel.url == url).exists()
            if cq:
                return True
            ch = CrawlHistoryModel.select().where(CrawlHistoryModel.url == url).exists()
            if ch:
                return True
            return False
        except Exception as e:
            logging.error(e)
            return False

    def add_crawl_history_database(self):
        logging.info(f"Adding items to crawl_history: {len(Overseer.crawl_history)}")
        with constants.CRAWL_HISTORY_LOCK:
            logging.debug(f"add_crawl_history_database locked for deepcopy")
            crawl_history = copy.deepcopy(Overseer.crawl_history)
            Overseer.crawl_history.clear()

        logging.debug(f"Processing crawl_history to add to database")
        crawl_history.sort(key=lambda x: x)
        unique_ids = list({x.domain[0].id: x for x in crawl_history}.values())
        for unique_id in unique_ids:
            domain_id = unique_id.domain[0].id
            crawl_history_processed = []
            timestamp = datetime.now()

            for url_domain in crawl_history:
                if url_domain.domain[0].id == domain_id:
                    crawl_history_processed.append(
                        {
                            "url": url_domain.url,
                            "timestamp": timestamp,
                            "http_status_code": url_domain.http_status_code,
                            "request_status": spider.Helper.request_status[
                                url_domain.request_status.name
                            ],
                            "domain_id": domain_id,
                        }
                    )
            try:
                (
                    CrawlHistoryModel.insert_many(crawl_history_processed)
                    .on_conflict(action="IGNORE")
                    .execute()
                )
                logging.info(f"Added {len(crawl_history_processed)} urls to crawl_history")
            except Exception as e:
                logging.info(
                    f"Failed to add {len(crawl_history_processed)} urls to crawl_history: {e}"
                )
        logging.info("Finished adding crawl_history to database")
