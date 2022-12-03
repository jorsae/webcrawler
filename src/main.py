from models import *
from spider import Spider

database.create_tables([DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])

spider = Spider(database)

robotsurl = spider.get_robots_url("https://www.youtube.com/watch?v=x2P7nDtXg-A")
print(robotsurl)