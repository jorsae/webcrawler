from models import DomainModel
from urllib.parse import urlparse
import logging

import constants

class UrlDomain:
    def __init__(self, url):
        self.url = url
        try:
            domain = urlparse(url).netloc
            with constants.DOMAIN_LOCK:
                self.domain = DomainModel.get_or_create(domain=domain)
        except Exception as e:
            self.domain = DomainModel.get_or_create(domain=url)
            logging.error(f'{url=} {self.domain=} {e}')
        self.http_status_code = -1
        self.request_status = -1
    
    def get_domain_id(self):
        try:
            return self.domain[0].id
        except Exception as e:
            logging.warning(f'{self} {e}')
            return -1

    def __eq__(self, other):
        if self.domain[0].id == other.domain[0].id:
            return True
        return False
    
    def __gt__(self, other):
        if self.domain[0].id > other.domain[0].id:
            return True
    
    def __lt__(self, other):
        try:
            if self.domain[0].id < other.domain[0].id:
                return True
        except Exception as e:
            logging.warning(f'{self} {e}')
            return True
    
    def __cmp__(self, other):
        if self.domain[0].id == other.domain[0].id:
            return 0
        elif self.domain[0].id > other.domain[0].id:
            return 1
        else:
            return -1
    
    def __str__(self):
        return f'{self.domain[0].id}: {self.url=}'