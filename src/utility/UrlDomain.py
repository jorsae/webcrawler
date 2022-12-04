from models import DomainModel
from urllib.parse import urlparse

class UrlDomain:
    def __init__(self, url):
        self.url = url
        domain = urlparse(url).netloc
        self.domain = DomainModel.get_or_create(domain=domain)
    

    def __eq__(self, other):
        if self.domain[0].id == other.domain[0].id:
            return True
        return False
    
    def __gt__(self, other):
        if self.domain[0].id > other.domain[0].id:
            return True
    
    def __lt__(self, other):
        if self.domain[0].id < other.domain[0].id:
            return True
    
    def __cmp__(self, other):
        if self.domain[0].id == other.domain[0].id:
            return 0
        elif self.domain[0].id > other.domain[0].id:
            return 1
        else:
            return -1


    def __str__(self):
        return f'{self.domain[0].id}: {self.url}'