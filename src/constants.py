import re
import threading

# Thread locks
CRAWL_QUEUE_LOCK = threading.Lock()
CRAWL_DATA_LOCK = threading.Lock()
CRAWL_HISTORY_LOCK = threading.Lock()
DOMAIN_MODEL_LOCK = threading.Lock()
CRAWL_EMAILS_LOCK = threading.Lock()
URL_STATUS_MODEL_LOCK = threading.Lock()
REQUEST_STATUS_MODEL_LOCK = threading.Lock()


DATABASE_FILE = 'webcrawler.db'
OVERSEER_RUN_DELAY = 1000 # ms


MAX_TIMEOUT = 5

MAX_URLS_IN_WORKER_QUEUE = 20

MAX_URLS_IN_CRAWL_QUEUE = 250
MAX_URLS_IN_CRAWL_HISTORY = 30

MAX_EMAILS_IN_EMAIL_QUEUE = 20
MAX_EMAILS_INSERTED_AT_ONCE = 999

REGEX_URL = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

REGEX_EMAIL_FETCH = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", re.IGNORECASE)