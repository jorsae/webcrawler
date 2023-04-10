import datetime
import logging
import os
import signal
import sys

import arguments
import constants
from commander import Commander
from models import *
from spider import Helper, Overseer
from utility import RequestStatus, UrlStatus

commander = None  # Commander object
last = datetime.datetime.now()  # Last time ctrl+c was triggered, for force killing.


def signal_handler(signal, frame):
    global last
    now = datetime.datetime.now()
    if (now - last) <= datetime.timedelta(seconds=1):
        print("Force killing process")
        sys.exit()

    last = datetime.datetime.now()
    commander.do_exit(None)
    sys.exit()


def main():
    global commander
    setup_logging()

    args = arguments.parse_arguments()
    overseer = Overseer(database)
    arguments.run_arguments(args, overseer)

    signal.signal(signal.SIGINT, signal_handler)  # signal handler for ctrl+c

    create_tables()
    fill_url_status_model()
    fill_request_status_model()

    Helper()  # initialize the url_status & request_status lists

    commander = Commander(overseer)
    commander.cmdloop()


def fill_request_status_model():
    with constants.REQUEST_STATUS_MODEL_LOCK:
        for request_status in RequestStatus:
            RequestStatusModel.get_or_create(request_status=request_status.name)
    logging.debug(f"Created {len(RequestStatus)} RequestStatus objects in db")


def fill_url_status_model():
    with constants.URL_STATUS_MODEL_LOCK:
        for url_status in UrlStatus:
            UrlStatusModel.get_or_create(url_status=url_status.name)
    logging.debug(f"Created {len(UrlStatus)} UrlStatus objects in db")


def create_tables():
    models = BaseModel.__subclasses__()
    database.create_tables(models)
    logging.debug(f"Created {len(models)} tables")


def setup_exit_handler():
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)


def exit_handler(a, e):
    print("application ending")


def setup_logging():
    logFolder = "./logs"
    logFile = "webcrawler.log"
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    handler = logging.FileHandler(filename=f"{logFolder}/{logFile}", encoding="utf-8", mode="a+")
    print_handler = logging.StreamHandler()
    logging.basicConfig(
        handlers=[handler],
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s",
    )


if __name__ == "__main__":
    main()
