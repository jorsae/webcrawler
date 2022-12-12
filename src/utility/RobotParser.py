import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse
import logging

from utility.UrlStatus import UrlStatus

class RobotParser:
    def __init__(self, id, robots_url):
        self.id = id
        self.robot_parser = None
        self.robots_url = robots_url
        try:
            self.domain = urlparse(robots_url).netloc
        except:
            self.domain = None
        self.url_status = UrlStatus.NOT_CHECKED
        self.url_status_updated = False
    
    def parse(self):
        self.robot_parser = rp.RobotFileParser()
        self.robot_parser.set_url(self.robots_url)
        try:
            self.robot_parser.read()
            self.domain = urlparse(self.robots_url).netloc
        except urllib.error.URLError as url_exception:
            logging.error(f'[{self.id}] Failed parsing robots: {self.robots_url}\t {url_exception}')
            return UrlStatus.SSL_VERIFICATION_FAILED
        except Exception as e:
            logging.error(f'[{self.id}] Failed parsing robots: {self.robots_url}\t {e}')
            return UrlStatus.ERROR
        
        logging.info(f'[{self.id}] Parsed robots: {self.robots_url}')
        return UrlStatus.OK
    
    def same_robot(self, url):
        try:
            if urlparse(url).netloc == self.domain:
                return True
            else:
                return False
        except:
            return False
    
    def can_fetch(self, url):
        if self.robot_parser is None:
            return False
        
        if self.robot_parser.can_fetch('*', url):
            return True
        return False
    
    def __str__(self):
        return f'{self.robots_url}, {self.domain}, {self.url_status}'