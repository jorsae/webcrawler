import logging
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

import constants
import processor
import spider
from models import CrawlDataModel, CrawlHistoryModel, CrawlQueueModel
from settings import Settings
from utility import RequestStatus, RobotParser, UrlDomain


class Worker:
    def __init__(self, database, id, run=True):
        self.database = database
        self.id = id
        self.queue = set()
        self.robot_parser = None
        self.domain = None
        self.harvested_urls = set()
        self.run = run
        self.current = None
        logging.debug("Created Worker")

    def crawl(self, start_url=None):
        logging.info(f"Worker {self.id} starting crawl | q: {len(self.queue)}")

        if start_url is not None:
            self.queue.add(start_url)

        while len(self.queue) > 0 and self.run:
            url_domain = UrlDomain(self.queue.pop())
            if url_domain is None:
                logging.error(f"[{self.id}] url_domain is None")
                continue
            self.ensure_robots_parsed(url_domain.url)
            logging.debug(f"{str(url_domain)=}")

            try:
                self.current = url_domain.url
                if self.robot_parser.can_fetch(url_domain.url) is False:
                    logging.debug(f"[{self.id}] Not allowed to crawl: {url_domain.url}")
                    url_domain.request_status = RequestStatus.NOT_ALLOWED
                else:
                    # Parsing http request + content
                    req = requests.get(url_domain.url, timeout=Settings.MAX_TIMEOUT)
                    url_domain.http_status_code = req.status_code
                    url_domain.request_status = RequestStatus.OK
                    harvested_urls = processor.url.get_urls(url_domain.url, req.text)
                    data = req.text

                    logging.debug(
                        f"[{self.id}] Added to Overseer.crawl_queue: {len(harvested_urls)} item(s)"
                    )
                    spider.Overseer.add_crawl_queue(harvested_urls)
                    self.add_crawl_history(url_domain, data)

                    emails = processor.url.get_emails(url_domain.url, req.text)
                    spider.Helper.add_crawl_email(emails)
            except requests.Timeout as ex_timeout:
                logging.warning(ex_timeout)
                url_domain.request_status = RequestStatus.TIMEOUT
            except requests.ConnectionError as ex_connection_error:
                logging.warning(ex_connection_error)
                url_domain.request_status = RequestStatus.CONNECTION_ERROR
            except requests.HTTPError as ex_http_error:
                logging.warning(ex_http_error)
                url_domain.request_status = RequestStatus.HTTP_ERROR
            except requests.URLRequired as ex_url_required:
                logging.warning(ex_url_required)
                url_domain.request_status = RequestStatus.URL_ERROR
            except Exception as e:
                logging.warning(e)
                url_domain.request_status = RequestStatus.ERROR

            # Deleting from queue
            self.remove_from_queue(url_domain.url)

            # Update the domain url_status
            if self.robot_parser.url_status_updated is False:
                self.robot_parser.url_status_updated = spider.Helper.update_domain_url_status(
                    self.robot_parser, self.domain
                )

            # Wait if website has a crawl-delay
            if self.robot_parser is not None:
                request_rate = self.robot_parser.robot_parser.request_rate("*")
                if request_rate is not None:
                    time.sleep(request_rate)

        # self.robot_parser = None
        logging.info(f"Worker {self.id} finished crawl: {self.run}")

    def add_crawl_history(self, url_domain, data):
        with constants.CRAWL_HISTORY_LOCK:
            crawl_history, crawl_history_created = CrawlHistoryModel.get_or_create(
                url=url_domain.url,
                timestamp=datetime.now(),
                http_status_code=url_domain.http_status_code,
                request_status=spider.Helper.request_status[url_domain.request_status.name],
                domain_id=url_domain.get_domain_id(),
            )
        if crawl_history_created is False:
            logging.error(f"Failed to add crawl_history to CrawlHistoryModel: {url_domain=}")

        with constants.CRAWL_DATA_LOCK:
            crawl_data, crawl_data_created = CrawlDataModel.get_or_create(
                data=data, crawl_history_id=crawl_history.id
            )
        if crawl_data_created is False:
            logging.error(f"Failed to add crawl_data to CrawlDataModel: {data=}")

    def remove_from_queue(self, url):
        try:
            with constants.CRAWL_QUEUE_LOCK:
                CrawlQueueModel.delete().where(CrawlQueueModel.url == url).execute()
        except Exception as e:
            logging.error(e)

    def ensure_robots_parsed(self, url):
        try:
            # If both passes, it's same url
            if self.robot_parser is not None:
                if self.robot_parser.same_robot(url):
                    return

            self.robot_parser = RobotParser(self.id, self.get_robots_url(url))
            self.robot_parser.url_status = self.robot_parser.parse()
            self.domain = UrlDomain(url)
        except Exception as e:
            logging.critical(e)

    def get_robots_url(self, url):
        try:
            uparse = urlparse(url)
            return f"{uparse.scheme}://{uparse.netloc}/robots.txt"
        except Exception as e:
            logging.error(e)
            return url
