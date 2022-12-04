import peewee as pw
import threading

from models import database, UrlStatusModel, RequestStatusModel
from spider import Spider, Worker

class Overseer:
    def __init__(self, database):
        self.database = database
        self.spiders = list()
        self.url_status = self.load_url_status()
        self.request_status = self.load_request_status()
    
    def start_spider(self, url):
        worker = Worker(database)
        spider = Spider(worker, None)
        self.spiders.append(spider)
    
    def load_url_status(self):
        return [url_status for url_status in UrlStatusModel.select()]
    
    def load_request_status(self):
        return [request_status for request_status in RequestStatusModel.select()]