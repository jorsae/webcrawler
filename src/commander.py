from models import *
from spider import Overseer, Helper
import utility.UrlStatus
import threading
import cmd
import constants

class Commander(cmd.Cmd):
    intro = 'Welcome to crawl-shell.   Type help or ? to list commands.\n'
    prompt = '(crawl-shell)$ '
    file = None
    
    def __init__(self, overseer):
        self.overseer = overseer
        self.overseer_thread = threading.Thread(target=self.overseer.run)
        self.overseer_thread.start()
        cmd.Cmd.__init__(self)
    
    def do_exit(self, arg):
        print('Stopping Spiders...')
        self.overseer.stop_all_spiders()
        
        print('Stopping Overseer...')
        self.overseer.run_overseer = False
        self.overseer_thread.join()
        
        print('Adding Crawl queue to database...')
        self.overseer.add_crawl_queue_database()
        return cmd.Cmd.postcmd(self, True, '')

    def do_spiders(self, arg):
        print(f'Overseer - t:{self.overseer_thread.is_alive()} / r:{self.overseer.run_overseer}')
        for spider in self.overseer.spiders:
            print(f'{spider}')
    
    def do_create_spider(self, arg):
        self.overseer.create_spider()
    
    def do_set_spider_url(self, arg):
        args = self.parse_args(arg)
        if len(args) != 2:
            print('set_spider_url takes 2 arguments: id url')
            return
        
        try:
            self.overseer.spiders[args[0]].worker.queue.add(args[1])
        except Exception as e:
            print(e)
    
    def do_start_spider(self, arg):
        args = self.parse_args(arg)
        
        spider = self.overseer.create_spider()
        if len(args) >= 1:
            self.overseer.start_spider(spider.id, args[0])
        else:
            self.overseer.start_spider(spider.id)
    
    def do_stop_spider(self, arg):
        args = self.parse_args(arg)
        if len(args) <= 0:
            print(f'stop_spider takes 1 arg: <id>')
        
        self.overseer.stop_spider(args[0])

    def do_stop_all(self, arg):
        self.overseer.stop_all_spiders()

    def do_list_queue(self, arg):
        print(f'{len(Overseer.crawl_queue)=} {len(Overseer.crawl_history)=} {len(Helper.crawl_emails)=}')
    
    def do_database_stats(self, arg):
        print('===== DATABASE STATS =====')
        # Can cause locked database.
        # url_status_id = UrlStatusModel.get(UrlStatusModel.url_status == utility.UrlStatus.OK.name)
        # print(f'Domains: {DomainModel.select().count():,} ({DomainModel.select().where(DomainModel.url_status_id == url_status_id).count():,})')
        # print(f'Domains: {DomainModel.select().count():,} ({DomainModel.select().where(DomainModel.url_status_id == url_status_id).count():,})')
        with constants.CRAWL_QUEUE_LOCK:
            print(f'Crawl Queue: {CrawlQueueModel.select().count():,}')
        with constants.CRAWL_HISTORY_LOCK:
            print(f'Crawl History: {CrawlHistoryModel.select().count():,}')
        with constants.CRAWL_DATA_LOCK:
            print(f'Crawl Data: {CrawlDataModel.select().count():,}')
        with constants.CRAWL_EMAILS_LOCK:
            print(f'Emails: {CrawlEmailModel.select().count():,}')
        # print(f'Requests Statuses: {RequestStatusModel.select().count():,} // Url Statuses: {UrlStatusModel.select().count():,}')
    
    def do_internal_stats(self, arg):
        print('===== INTERNAL STATS =====')
        print(f'Crawl Queue: {len(Overseer.crawl_queue)} / {constants.MAX_URLS_IN_CRAWL_QUEUE}')
        print(f'Crawl History: {len(Overseer.crawl_history)} / {constants.MAX_URLS_IN_CRAWL_HISTORY}')
        print(f'Crawl Emails: {len(Helper.crawl_emails)} / {constants.MAX_EMAILS_IN_EMAIL_QUEUE}\tchunks:({constants.MAX_EMAILS_INSERTED_AT_ONCE})')
    
    def do_stats(self, arg):
        self.do_internal_stats(arg)
        self.do_database_stats(arg)
    
    def parse_args(self, args):
        args = args.split(' ')

        for i in range(len(args)):
            try:
                args[i] = int(args[i])
            except:
                pass
        return args