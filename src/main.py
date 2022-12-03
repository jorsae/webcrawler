from models import *
from spider import Spider

database.create_tables([UrlCodeModel, DomainModel, CrawlQueueModel, CrawlHistoryModel, CrawlEmailModel])

spider = Spider(database)

robots_url = spider.get_robots_url("https://www.minerals.org.au/")
robots_url = spider.get_robots_url("https://www.usa.gov/robots.txt")
print(robots_url)

print(spider.parse_robots(robots_url))


# TODO: Find robots file with a request delay to test it