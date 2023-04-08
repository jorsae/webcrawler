from models import UrlStatusModel, RequestStatusModel, DomainModel, CrawlEmailModel
import logging
from datetime import datetime

import spider
import constants

class Helper:

    url_status = None
    request_status = None

    @staticmethod
    def load_url_status():
        url_status_dict = {}
        with constants.URL_STATUS_MODEL_LOCK:
            url_status = list(UrlStatusModel.select())
        for us in url_status:
            url_status_dict[us.url_status] = us.id
        logging.debug(f'loaded {len(url_status)} url_statuses')
        return url_status_dict
    
    @staticmethod
    def load_request_status():
        request_status_dict = {}
        with constants.REQUEST_STATUS_MODEL_LOCK:
            request_status = list(RequestStatusModel.select())
        for rs in request_status:
            request_status_dict[rs.request_status] = rs.id
        
        logging.debug(f'Loaded {len(request_status)} request_statuses')
        return request_status_dict
    
    @staticmethod
    def update_domain_url_status(robot_parser, domain):
        try:
            with constants.DOMAIN_MODEL_LOCK:
                # TODO: if url_status is SSL_VERIFICATION_FAILED or ERROR. Do something?
                url_status = spider.Helper.url_status[robot_parser.url_status.name]
                (DomainModel
                    .update({DomainModel.url_status_id: url_status})
                    .where(DomainModel.id == domain.get_domain_id())
                    .execute()
                )
            return True
        except Exception as e:
            logging.error(e)
            return False
    
    crawl_emails = list()
    @staticmethod
    def add_crawl_email(value):
        try:
            with constants.CRAWL_EMAILS_LOCK:
                if type(value) == list:
                    Helper.crawl_emails += value
                else:
                    Helper.crawl_emails.append(value)
            if len(Helper.crawl_emails) > constants.MAX_EMAILS_IN_EMAIL_QUEUE:
                Helper.add_crawl_email_database()
        except Exception as e:
            logging.error(f'Failed to add items to crawl_emails: {e}')
    
    def add_crawl_email_database():
        with constants.CRAWL_EMAILS_LOCK:
            while len(Helper.crawl_emails) > 0:
                emails = 0
                email_objects = []
                now = datetime.now()
                for email in Helper.crawl_emails:
                    Helper.crawl_emails.remove(email)
                    if emails > constants.MAX_EMAILS_INSERTED_AT_ONCE:
                        break
                    email_objects.append(
                        {
                        'email': email,
                        'timestamp': now
                        })
                    emails += 1
                try:
                    mass_insert_query = (CrawlEmailModel
                                            .insert_many(email_objects)
                                            .on_conflict(action='IGNORE')
                                            .as_rowcount()
                                            .execute()
                                        )
                    logging.info(f'Inserted {mass_insert_query} emails to crawl_email. {len(Helper.crawl_emails)=}')
                except Exception as e:
                    logging.error(f'Failed to add emails to crawl_email: {e}')
    
    def __init__(self):
        spider.Helper.url_status = self.load_url_status()
        spider.Helper.request_status = self.load_request_status()