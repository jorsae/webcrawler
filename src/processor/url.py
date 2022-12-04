from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin

re_url = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def get_urls(url, content):
    soup = BeautifulSoup(content, "lxml")
    urls = []
    for link in soup.findAll('a', href=True):
        link = urljoin(url, link['href'])
        if re.match(re_url, link) is not None:
            urls.append(link)
    return urls