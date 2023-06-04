import argparse

from models import database
from settings import Settings


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database", "-d", type=str, default="webcrawler.db", help="Database file"
    )
    parser.add_argument(
        "--threads", "-t", type=int, default=0, help="Spider threads to start with"
    )
    return parser.parse_args()


def run_arguments(args, overseer):
    Settings.DATABASE_FILE = args.database
    database.init(args.database)

    for i in range(args.threads):
        spider = overseer.create_spider()
        overseer.start_spider(spider.id)
