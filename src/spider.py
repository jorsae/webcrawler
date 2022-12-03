import peewee as pw
import urllib.robotparser as rp
from urllib.parse import urlparse

class Spider:
    def __init__(self, database):
        self.database = database
        self.queue = set()
        self.rp_parser = None
    
    def get_robots_url(self, url):
        uparse = urlparse(url)
        return f'{uparse.scheme}://{uparse.netloc}/robots.txt'