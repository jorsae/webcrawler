class Spider:
    def __init__(self, worker, thread=None):
        # TODO: Add other stats, such as start_time, should_run, etc.
        self.worker = worker
        self.thread = thread