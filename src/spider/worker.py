import peewee as pw
import logging
import requests
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse
from datetime import datetime

from models import CrawlQueueModel, DomainModel, UrlStatusModel
import spider
from utility.UrlStatus import UrlStatus
from utility.RequestStatus import RequestStatus
from utility.UrlDomain import UrlDomain
import processor

class Worker:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.robot_parser = None
        self.last_robots_domain = ''
        self.domain = None
        self.harvested_urls = set()
        self.crawl_history = []
        logging.debug('Created Worker')
    
    def crawl(self, start_url = None):
        logging.info('Worker starting crawl')
        if start_url is not None:
            self.queue.add(start_url)
        
        while len(self.queue) > 0:
            url_domain = UrlDomain(self.queue.pop())
            self.ensure_robots_parsed(url_domain.url)
            try:
                req = requests.get(url_domain.url)
                url_domain.http_status_code = req.status_code
                url_domain.request_status = RequestStatus.OK
                harvested_urls = processor.url.get_urls(url_domain.url, req.text)
                spider.Overseer.add_crawl_queue(harvested_urls)
            except requests.Timeout:
                url_domain.request_status = RequestStatus.OK
            except requests.ConnectionError:
                url_domain.request_status = RequestStatus.CONNECTION_ERROR
            except requests.HTTPError:
                url_domain.request_status = RequestStatus.HTTP_ERROR
            except requests.URLRequired:
                url_domain.request_status = RequestStatus.URL_ERROR
            except Exception as e:
                url_domain.request_status = RequestStatus.ERROR
            
            # Adding to crawl_history, deleting from crawl_queue
            spider.Overseer.add_crawl_history(url_domain)
            CrawlQueueModel.delete().where(CrawlQueueModel.url == url_domain.url).execute()
        logging.info('Worker finished crawl')
    
    def ensure_robots_parsed(self, url):
        if urlparse(url).netloc != self.last_robots_domain:
            robots_url = self.get_robots_url(url)
            url_status = self.parse_robots(robots_url)
            # TODO: Add url_status_id to UrlDomain
            self.domain = UrlDomain(url)
    
    def get_robots_url(self, url):
        uparse = urlparse(url)
        return f'{uparse.scheme}://{uparse.netloc}/robots.txt'
    
    def parse_robots(self, robots_url):
        self.robot_parser = rp.RobotFileParser()
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()
            self.last_robots_domain = urlparse(robots_url).netloc
        except urllib.error.URLError as url_exception:
            logging.error(f'Failed parsing robots: {robots_url}\t {url_exception}')
            return UrlStatus.SSL_VERIFICATION_FAILED
        except Exception as e:
            logging.error(f'Failed parsing robots: {robots_url}\t {e}')
            return UrlStatus.ERROR
        
        logging.info(f'Parsed robots: {robots_url}')
        return UrlStatus.OK