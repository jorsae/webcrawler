import peewee as pw
import requests
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse

from utility.UrlCode import UrlCode
import processor

class Spider:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.robot_parser = None
        self.last_robots_domain = ''
    
    def crawl(self, start_url = None):
        if start_url is not None:
            self.queue.add(start_url)
        
        while len(self.queue) > 0:
            url = self.queue.pop()
            print(url)
            req = requests.get(url)
            urls = processor.url.get_urls(url, req.text)
            for u in urls:
                self.queue.add(u)
    
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