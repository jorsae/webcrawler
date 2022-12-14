from models import *
from spider import Overseer
import threading
import cmd

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
        print('Stopping spiders...')
        self.overseer.stop_all_spiders()
        
        print('Stopping Overseer..')
        self.overseer.run_overseer = False
        self.overseer_thread.join()
        
        print('Adding Crawl queue to database..')
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
        print(f'{len(Overseer.crawl_queue)=} {len(Overseer.crawl_history)=}')
    
    def parse_args(self, args):
        args = args.split(' ')

        for i in range(len(args)):
            try:
                args[i] = int(args[i])
            except:
                pass
        return args