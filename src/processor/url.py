import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import constants
from utility import UrlDomain


def get_urls(url, content):
    try:
        logging.debug(f"get_urls Processing: {url}")
        soup = BeautifulSoup(content, "html.parser")
        urls = []
        for link in soup.findAll("a", href=True):
            link = urljoin(url, link["href"])
            if re.match(constants.REGEX_URL, link) is not None:
                urls.append(UrlDomain(link))

        return urls
    except Exception as e:
        logging.error(e)
        return []


def get_emails(url, content):
    # TODO: Remove duplicate
    return re.findall(constants.REGEX_EMAIL_FETCH, content)
