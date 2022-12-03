import peewee as pw
import urllib.robotparser as rp
from urllib.parse import urlparse

class Spider:
    def __init__(database):
        self.database = database
        self.queue = set()
        self.rp_parser = None
    
    def get_robots_url(url):
        pass