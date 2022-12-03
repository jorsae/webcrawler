from models import *

database.create_tables([DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])