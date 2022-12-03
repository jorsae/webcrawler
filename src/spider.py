import peewee as pw
import urllib
import urllib.robotparser as rp
from urllib.parse import urlparse

from utility.UrlCode import UrlCode

class Spider:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.robot_parser = None
    
    def get_robots_url(self, url):
        uparse = urlparse(url)
        return f'{uparse.scheme}://{uparse.netloc}/robots.txt'
    
    def parse_robots(self, robots_url):
        self.robot_parser = rp.RobotFileParser()
        self.robot_parser.set_url(robots_url)
        try:
            self.robot_parser.read()
        except urllib.error.URLError as e:
            return UrlCode.SSL_VERIFICATION_FAILED
        except:
            return UrlCode.ERROR
        
        rrate = self.robot_parser.request_rate('*')
        print(self.robot_parser.crawl_delay('*'))
        return UrlCode.OK