import logging
import requests
import time
from urllib.parse import urlparse

from models import CrawlQueueModel, DomainModel
import spider
from utility.UrlStatus import UrlStatus
from utility.RequestStatus import RequestStatus
from utility.UrlDomain import UrlDomain
from utility.RobotParser import RobotParser
import processor

class Worker:
    def __init__(self, database, id):
        self.database = database
        self.id = id
        self.queue = set()
        self.robot_parser = None
        self.last_robots_domain = ''
        self.domain = None
        self.harvested_urls = set()
        self.crawl_history = []
        logging.debug('Created Worker')
    
    def crawl(self, start_url = None):
        logging.info(f'Worker {self.id} starting crawl')
        
        if start_url is not None:
            self.queue.add(start_url)
        
        while len(self.queue) > 0:
            url_domain = UrlDomain(self.queue.pop())
            self.ensure_robots_parsed(url_domain.url)
            try:
                if self.robot_parser.can_fetch(url_domain.url) is False:
                    logging.debug(f'[{self.id}] Not allowed to crawl: {url_domain.url}')
                    url_domain.request_status = RequestStatus.NOT_ALLOWED
                    continue
                
                # Parsing http request + content
                req = requests.get(url_domain.url)
                url_domain.http_status_code = req.status_code
                url_domain.request_status = RequestStatus.OK
                harvested_urls = processor.url.get_urls(url_domain.url, req.text)
                spider.Overseer.add_crawl_queue(harvested_urls)
                
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
            
            # Adding to crawl_history
            spider.Overseer.add_crawl_history(url_domain)
            
            # Deleting from queue
            self.remove_from_queue(url_domain.url)
            
            # Update the domain url_status
            if self.robot_parser.url_status_updated is False:
                self.robot_parser.url_status_updated = spider.Helper.update_domain_url_status(self.robot_parser, self.domain)

            # Wait if website has a crawl-delay
            if self.robot_parser is not None:
                request_rate = self.robot_parser.robot_parser.request_rate('*')
                if request_rate is not None:
                    time.sleep(request_rate)
        
        logging.info(f'Worker {self.id} finished crawl')
    
    def remove_from_queue(self, url):
        try:
            CrawlQueueModel.delete().where(CrawlQueueModel.url == url).execute()
        except Exception as e:
            logging.error(e)
    
    def ensure_robots_parsed(self, url):
        # If both passes, it's same url
        if self.robot_parser is not None:
            if self.robot_parser.same_robot(url):
                return
        
        self.robot_parser = RobotParser(self.id, self.get_robots_url(url))
        self.robot_parser.url_status = self.robot_parser.parse()
        self.domain = UrlDomain(url)
    
    def get_robots_url(self, url):
        try:
            uparse = urlparse(url)
            return f'{uparse.scheme}://{uparse.netloc}/robots.txt'
        except Exception as e:
            logging.error(e)
            return url