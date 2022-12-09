from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin

from utility.UrlDomain import UrlDomain
import constants

def get_urls(url, content):
    logging.debug(f'get_urls Processing: {url}')
    soup = BeautifulSoup(content, "html.parser")
    urls = []
    for link in soup.findAll('a', href=True):
        link = urljoin(url, link['href'])
        if re.match(constants.REGEX_URL, link) is not None:
            urls.append(UrlDomain(link))
    
    return urls

def get_emails(url, content):
    return re.findall(constants.REGEX_EMAIL_FETCH, content)