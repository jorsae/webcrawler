import logging

class Spider:
    def __init__(self, worker, id, thread=None):
        # TODO: Add other stats, such as start_time, should_run, etc.
        self.worker = worker
        self.id = id
        self.thread = thread
        logging.debug('Created Spider')
    
    def stop_worker(self):
        self.worker.run = False

    def stop_thread(self):
        if self.worker.run:
            self.worker.run = False
        self.thread.join()

    def __str__(self):
        return f'[{self.id}] thread:{self.thread.is_alive()}/run:{self.worker.run} - {self.worker.domain}'