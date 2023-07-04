import cmd
import logging
import threading

import constants
import processor
import utility.UrlStatus
from models import *
from settings import Settings
from spider import Helper, Overseer


class Commander(cmd.Cmd):
    intro = "Welcome to crawl-shell.   Type help or ? to list commands.\n"
    prompt = "(crawl-shell)$ "
    file = None

    def __init__(self, overseer):
        self.overseer = overseer
        self.overseer_thread = threading.Thread(target=self.overseer.run)
        self.overseer_thread.start()
        cmd.Cmd.__init__(self)

    def do_exit(self, arg):
        "Gracefully exit webcrawler"
        print("Stopping Spiders...")
        self.overseer.stop_all_spiders()

        print("Stopping Overseer...")
        self.overseer.run_overseer = False
        self.overseer_thread.join()

        print("Adding Crawl Queue to database...")
        self.overseer.add_crawl_queue_database()
        print("Adding Crawl History to database...")
        self.overseer.add_crawl_history_database()
        print("Adding Crawl Emails to database...")
        Helper.add_crawl_email_database()
        return cmd.Cmd.postcmd(self, True, "")

    def do_spiders(self, arg):
        "Overview of all Spiders. e.g.: spiders"
        print(f"\tOverseer - t:{self.overseer_thread.is_alive()} / r:{self.overseer.run_overseer}")
        for spider in self.overseer.spiders:
            print(f"{spider}")

    def do_set_spider_url(self, arg):
        "Set url for a spider. e.g.: set_spider_url <id> <url>"
        args = self.parse_args(arg)
        if len(args) != 2:
            print("set_spider_url takes 2 arguments: id url")
            return

        try:
            self.overseer.spiders[args[0]].worker.queue.add(args[1])
        except Exception as e:
            print(e)

    def do_start_spider(self, arg):
        "Start a spider. e.g.: start_spider (id)"
        args = self.parse_args(arg)

        if type(args[0]) == int:
            started_spider = self.overseer.start_spider(args[0])
        else:
            spider = self.overseer.create_spider()
            started_spider = self.overseer.start_spider(spider.id)

        if started_spider is False:
            print("Unable to start spider")

    def do_stop_spider(self, arg):
        "Stop a spider. e.g.: stop_spider <id>"
        args = self.parse_args(arg)
        if len(args) <= 0:
            print(f"stop_spider takes 1 arg: <id>")

        self.overseer.stop_spider(args[0])

    def do_start_all(self, arg):
        "Start all spiders. e.g.: start_all"
        self.overseer.start_all_spiders()

    def do_stop_all(self, arg):
        "Stop all spiders. e.g.: stop_all"
        self.overseer.stop_all_spiders()

    def do_stats(self, arg):
        "Display all stats"
        self.internal_stats(arg)
        self.database_stats(arg)

    def internal_stats(self, arg):
        "Display internal runtime stats"
        print("===== INTERNAL STATS =====")
        print(f"Crawl Queue: {len(Overseer.crawl_queue)} / {Settings.MAX_URLS_IN_CRAWL_QUEUE}")
        print(
            f"Crawl History: {len(Overseer.crawl_history)} / {Settings.MAX_URLS_IN_CRAWL_HISTORY}"
        )
        print(
            f"Crawl Emails: {len(Helper.crawl_emails)} / {Settings.MAX_EMAILS_IN_EMAIL_QUEUE}\tchunks:({Settings.MAX_EMAILS_INSERTED_AT_ONCE})"
        )

    def database_stats(self, arg):
        "Display database stats"
        print("===== DATABASE STATS =====")
        # Can cause locked database.
        with constants.URL_STATUS_MODEL_LOCK:
            url_status_id = UrlStatusModel.get(
                UrlStatusModel.url_status == utility.UrlStatus.OK.name
            )
        with constants.DOMAIN_MODEL_LOCK:
            print(
                f"Domains: {DomainModel.select().count():,} ({DomainModel.select().where(DomainModel.url_status_id == url_status_id).count():,})"
            )
        with constants.CRAWL_QUEUE_LOCK:
            print(f"Crawl Queue: {CrawlQueueModel.select().count():,}")
        with constants.CRAWL_HISTORY_LOCK:
            print(f"Crawl History: {CrawlHistoryModel.select().count():,}")
        with constants.CRAWL_DATA_LOCK:
            print(f"Crawl Data: {CrawlDataModel.select().count():,}")
        with constants.CRAWL_EMAILS_LOCK:
            print(f"Emails: {CrawlEmailModel.select().count():,}")

        with constants.REQUEST_STATUS_MODEL_LOCK:
            request_statuses = f"Requests Statuses: {RequestStatusModel.select().count():,}"
        with constants.URL_STATUS_MODEL_LOCK:
            url_statuses = f"Url Statuses: {UrlStatusModel.select().count():,}"
        print(f"{request_statuses} // {url_statuses}")

    def do_settings(self, arg):
        "Display all settings"
        print("===== SETTINGS =====")
        print(f"Database: {Settings.DATABASE_FILE}")
        print(f"Overseer run: {Settings.OVERSEER_RUN_DELAY}ms")
        print(f"Request Timeout: {Settings.MAX_TIMEOUT}")
        print(
            f"Urls in worker queue: {Settings.MIN_URLS_IN_WORKER_QUEUE}-{Settings.MAX_URLS_IN_WORKER_QUEUE}"
        )
        print(f"Max Crawl Queue: {Settings.MAX_URLS_IN_CRAWL_QUEUE}")
        print(f"Max History: {Settings.MAX_URLS_IN_CRAWL_HISTORY}")
        print(
            f"Max emails: {Settings.MAX_EMAILS_IN_EMAIL_QUEUE}\tChunks: {Settings.MAX_EMAILS_INSERTED_AT_ONCE}"
        )

    def do_deepsettings(self, arg):
        "Display internal runtime settings"
        print(f"{Settings.SETTINGS_FILE=}")
        print(
            f"{Settings.LOG_LEVEL=} / {Settings.translate_loglevel(logging.getLogger().getEffectiveLevel())}"
        )
        print(f"{Settings.DATABASE_FILE=}")
        print(f"{Settings.OVERSEER_RUN_DELAY=}")
        print(f"{Settings.MAX_TIMEOUT=}")
        print(f"{Settings.MIN_URLS_IN_WORKER_QUEUE=}")
        print(f"{Settings.MAX_URLS_IN_WORKER_QUEUE=}")
        print(f"{Settings.MAX_URLS_IN_CRAWL_QUEUE=}")
        print(f"{Settings.MAX_URLS_IN_CRAWL_HISTORY=}")
        print(f"{Settings.MAX_EMAILS_IN_EMAIL_QUEUE=}")
        print(f"{Settings.MAX_EMAILS_INSERTED_AT_ONCE=}")

    def do_change(self, arg):
        "Change a setting. e.g.: change <setting_name> <value>"
        args = self.parse_args(arg)
        if len(args) != 2:
            print("csettings takes 2 arguments: setting_name value")
            return

        setting_name = args[0]
        value = args[1]
        updated = Settings.update_setting(setting_name, value)

        if updated is False:
            print(f"Failed to update setting: {setting_name} to {value}")

    def do_save(self, arg):
        "Save settings to a file"
        saved = Settings.save_settings()
        if saved is False:
            print("Failed to save settings")

    def do_reload(self, arg):
        "Reloads settings from a file"
        reloaded = Settings.parse_settings()
        if reloaded is False:
            print("Failed to reload settings")

    def do_summary(self, arg):
        "Outputs a summary of crawl data. e.g.: summary <id>"
        args = self.parse_args(arg)
        if len(args) != 1:
            print("summary takes 1 argument: id")
            return

        with constants.CRAWL_DATA_LOCK:
            data = CrawlDataModel.select().where(CrawlDataModel.crawl_history_id == args[0]).get()
        summary = processor.data.get_summarization(data.data)
        print(summary)

    def parse_args(self, args):
        args = args.split(" ")

        for i in range(len(args)):
            try:
                args[i] = int(args[i])
            except:
                pass
        return args
