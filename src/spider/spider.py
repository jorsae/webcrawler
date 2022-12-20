import logging

class Spider:
    def __init__(self, worker, id, thread=None):
        # TODO: Add other stats, such as start_time, should_run, etc.
        self.worker = worker
        self.id = id
        self.thread = thread
        logging.debug('Created Spider')
    
    def __str__(self):
        return f'[{self.id}] r: {self.thread.is_alive()}/{self.worker.run} - {self.worker.domain}'