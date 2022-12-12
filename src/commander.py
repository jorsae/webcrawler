from models import *
from spider import Overseer
import threading
import cmd

class Commander(cmd.Cmd):
    intro = 'Welcome to crawl-shell.   Type help or ? to list commands.\n'
    prompt = '(crawl-shell)$ '
    file = None
    
    overseer = Overseer(database)
    overseer_thread = threading.Thread(target=overseer.run)
    overseer_thread.start()
    
    def do_spiders(self, arg):
        for spider in self.overseer.spiders:
            print(f'{spider.id}: {spider.worker.domain} {spider.thread.is_alive()}')
    
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
    
    def do_restart_spider(self, arg):
        args = self.parse_args(arg)
        
        spider = None
        for s in self.overseer.spiders:
            if s.id == args[0]:
                spider = s
        
        print(spider.worker.robot_parser)
        if spider is None:
            print('no spider found')
        
        self.overseer.get_spider_urls(spider)
        spider_queue = len(spider.worker.queue)
        print(f'{spider_queue} @ {spider.thread.is_alive()}')
        self.overseer.start_spider(spider.id)
        print(f'{len(spider.worker.queue)} @ {spider.thread.is_alive()}')
        print(spider.worker.robot_parser)

    def do_list_queue(self, arg):
        print(f'{len(Overseer.crawl_queue)=} {len(Overseer.crawl_history)=}')
    
    def parse_args(self, args):
        args = args.split(' ')

        for i in range(len(args)):
            try:
                args[i] = int(args[i])
            except:
                pass
        return args