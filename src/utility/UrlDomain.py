from models import DomainModel
from urllib.parse import urlparse

class UrlDomain:
    def __init__(self, url, url_status_id=4):
        try:
            self.url = url
            domain = urlparse(url).netloc
            self.domain = DomainModel.get_or_create(domain=domain, url_status_id=url_status_id)
        except Exception as e:
            print('AAAAAAAAAAAAAAAA')
            print(e)