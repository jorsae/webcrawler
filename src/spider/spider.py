import logging

class Spider:
    def __init__(self, worker, id, thread=None):
        # TODO: Add other stats, such as start_time, should_run, etc.
        self.worker = worker
        self.id = id
        self.thread = thread
        self.stop = False # Used to user-control to manually stop the spider
        logging.debug('Created Spider')
    
    def stop_worker(self):
        self.worker.run = False

    def stop_thread(self):
        if self.worker.run:
            self.worker.run = False
        self.thread.join()

    def __str__(self):
        if self.stop:
            return f'[{self.id}](PAUSED) Q:{len(self.worker.queue)}/Urls:{len(self.worker.harvested_urls)}/History:{len(self.worker.crawl_history)}  thread:{self.thread.is_alive()}/run:{self.worker.run} - {self.worker.domain} - {self.worker.current}'
        return f'[{self.id}] Q:{len(self.worker.queue)}/Urls:{len(self.worker.harvested_urls)}/History:{len(self.worker.crawl_history)}  thread:{self.thread.is_alive()}/run:{self.worker.run} - {self.worker.domain} - {self.worker.current}'