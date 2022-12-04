import peewee as pw
import requests
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse
from datetime import datetime

from models import CrawlQueueModel, DomainModel, UrlStatusModel
from utility.UrlStatus import UrlStatus
import processor

class Worker:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.robot_parser = None
        self.last_robots_domain = ''
        self.domain = None
        self.crawl_history = []
    
    def crawl(self, start_url = None):
        if start_url is not None:
            self.queue.add(start_url)
        
        while len(self.queue) > 0:
            url = self.queue.pop()
            self.ensure_parsed(url)
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
    
    def ensure_parsed(self, url):
        if urlparse(url).netloc is not self.last_robots_domain:
            robots_url = self.get_robots_url(url)
            url_status = self.parse_robots(robots_url)
            url_status_id = (UrlStatusModel
                            .select(UrlStatusModel.id)
                            .where(UrlStatusModel.url_status == url_status.name)
                            .get())
            self.domain = DomainModel.get_or_create(domain=self.last_robots_domain, url_status_id=url_status_id)
            print(f'{self.domain=}')

    def store_urls(self, urls):
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
            return UrlStatus.SSL_VERIFICATION_FAILED
        except:
            return UrlStatus.ERROR
        return UrlStatus.OK