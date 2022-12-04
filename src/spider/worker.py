import peewee as pw
import logging
import requests
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse
from datetime import datetime

from models import CrawlQueueModel, DomainModel, UrlStatusModel
from utility.UrlStatus import UrlStatus
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
            url = self.queue.pop()
            self.ensure_robots_parsed(url)
            try:
                req = requests.get(url)
            except requests.Timeout:
                continue
            except requests.ConnectionError:
                continue
            except requests.HTTPError:
                continue
            except requests.URLRequired:
                continue
            except Exception as e:
                continue
            
            urls = processor.url.get_urls(url, req.text)
            self.store_urls(urls)
            self.crawl_history.append(url)
        logging.info('Worker finished crawl')
    
    def ensure_robots_parsed(self, url):
        if urlparse(url).netloc != self.last_robots_domain:
            robots_url = self.get_robots_url(url)
            url_status = self.parse_robots(robots_url)
            url_status_id = (UrlStatusModel
                            .select(UrlStatusModel.id)
                            .where(UrlStatusModel.url_status == url_status.name)
                            .get())
            self.domain = UrlDomain(url)
    
    def store_urls(self, urls):
        # TODO: Make this sort and bulk insert
        for url in urls:
            domain = urlparse(url).netloc
            domain = DomainModel.get_or_create(domain=domain)
            print(domain[0].id)
            (CrawlQueueModel
                .insert(url=url, priority=0, timestamp=datetime.now(), domain_id=domain[0])
                .on_conflict(action='IGNORE')
                .execute()
            )
        return

        crawl_queue = []
        timestamp = datetime.now()
        for url in urls:
            crawl_queue.append(
                {
                    'url': url,
                    'priority': 0,
                    'timestamp': timestamp,
                    'domain_id': self.domain[0]
                })
        try:
            (CrawlQueueModel
                .insert_many(crawl_queue)
                .on_conflict(action='IGNORE')
                .execute())
            logging.info(f'Added {len(crawl_queue)} urls to crawl_queue')
        except Exception as e:
            logging.info(f'Failed to add {len(crawl_queue)} urls to crawl_queue: {e}')

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