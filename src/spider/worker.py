import peewee as pw
import requests
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse
from datetime import datetime

from models import CrawlQueueModel, DomainModel, UrlCodeModel
from utility.UrlCode import UrlCode
import processor

class Worker:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.robot_parser = None
        self.last_robots_domain = ''
        self.domain = None
    
    def crawl(self, start_url = None):
        if start_url is not None:
            self.queue.add(start_url)
        
        while len(self.queue) > 0:
            url = self.queue.pop()
            self.ensure_parsed(url)
            
            req = requests.get(url)
            urls = processor.url.get_urls(url, req.text)
            self.store_urls(urls)
    
    def ensure_parsed(self, url):
        if urlparse(url).netloc is not self.last_robots_domain:
            robots_url = self.get_robots_url(url)
            url_code = self.parse_robots(robots_url)
            url_code_id = (UrlCodeModel
                            .select(UrlCodeModel.id)
                            .where(url_code == url_code))
            self.domain = DomainModel.get_or_create(domain=self.last_robots_domain, url_code_id=url_code_id)

    def store_urls(self, urls):
        crawl_queue = []

        for url in urls:
            crawl_queue.append(
                {
                    'url': url,
                    'priority': 0,
                    'timestamp': datetime.now(),
                    'domain_id': self.domain[0]
                })
        try:
            CrawlQueueModel.insert_many(crawl_queue).execute()
        except Exception as e:
            print(e)

    def get_robots_url(self, url):
        uparse = urlparse(url)
        return f'{uparse.scheme}://{uparse.netloc}/robots.txt'
    
    def parse_robots(self, robots_url):
        self.robot_parser = rp.RobotFileParser()
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()
            self.last_robots_domain = urlparse(robots_url).netloc
        except urllib.error.URLError:
            return UrlCode.SSL_VERIFICATION_FAILED
        except:
            return UrlCode.ERROR
        return UrlCode.OK