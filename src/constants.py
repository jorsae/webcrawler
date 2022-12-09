import re

DATABASE_FILE = 'webcrawler.db'

MAX_URLS_IN_WORKER_QUEUE = 20

MAX_URLS_IN_CRAWL_QUEUE = 0
MAX_URLS_IN_CRAWL_HISTORY = 0

MAX_EMAILS_IN_EMAIL_QUEUE = 0

REGEX_URL = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

REGEX_EMAIL_FETCH = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", re.IGNORECASE)