from models import UrlStatusModel, RequestStatusModel
import logging

import spider

class Helper:
    url_status = None
    request_status = None

    @staticmethod
    def load_url_status():
        url_status_dict = {}
        url_status = list(UrlStatusModel.select())
        for us in url_status:
            url_status_dict[us.url_status] = us.id
        logging.debug(f'loaded {len(url_status)} url_statuses')
        return url_status_dict
    
    @staticmethod
    def load_request_status():
        request_status_dict = {}
        request_status = list(RequestStatusModel.select())
        for rs in request_status:
            request_status_dict[rs.request_status] = rs.id
        
        logging.debug(f'Loaded {len(request_status)} request_status')
        return request_status_dict
    
    def __init__(self):
        spider.Helper.url_status = self.load_url_status()
        spider.Helper.request_status = self.load_request_status()