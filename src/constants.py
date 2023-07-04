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

# Regex
REGEX_URL = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)
REGEX_EMAIL_FETCH = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", re.IGNORECASE)
