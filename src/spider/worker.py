import logging
import requests
import time
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse

from models import CrawlQueueModel
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
                if self.robot_parser.can_fetch('*', url_domain.url):
                    req = requests.get(url_domain.url)
                    url_domain.http_status_code = req.status_code
                    url_domain.request_status = RequestStatus.OK
                    harvested_urls = processor.url.get_urls(url_domain.url, req.text)
                    spider.Overseer.add_crawl_queue(harvested_urls)
                else:
                    url_domain.request_status = RequestStatus.NOT_ALLOWED
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
            
            # Wait, if website has a crawl-delay
            request_rate = self.robot_parser.request_rate('*')
            if request_rate is not None:
                time.sleep(request_rate)
        
        logging.info('Worker finished crawl')
    
    def remove_from_queue(self, url):
        try:
            CrawlQueueModel.delete().where(CrawlQueueModel.url == url).execute()
        except Exception as e:
            logging.error(e)
    
    def ensure_robots_parsed(self, url):
        try:
            if urlparse(url).netloc != self.last_robots_domain:
                robots_url = self.get_robots_url(url)
                url_status = self.parse_robots(robots_url)
                # TODO: Add url_status_id to UrlDomain
                self.domain = UrlDomain(url)
        except Exception as e:
            logging.error(e)
    
    def get_robots_url(self, url):
        try:
            uparse = urlparse(url)
            return f'{uparse.scheme}://{uparse.netloc}/robots.txt'
        except Exception as e:
            logging.error(e)
            return url
    
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