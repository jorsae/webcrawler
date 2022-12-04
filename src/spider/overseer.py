import peewee as pw
import threading

from models import database
from spider import Spider, Worker

class Overseer:
    def __init__(self):
        self.spiders = list()
    
    def start_spider(self, url):
        worker = Worker(database)
        spider = Spider(worker, None)
        
        self.spiders.append(spider)