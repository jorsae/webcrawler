import json
import logging


class Settings:
    SETTINGS_FILE = "settings.json"
    DATABASE_FILE = "webcrawler.db"

    OVERSEER_RUN_DELAY = 1000  # ms
    MAX_TIMEOUT = 5
    MIN_URLS_IN_WORKER_QUEUE = 3
    MAX_URLS_IN_WORKER_QUEUE = 20
    MAX_URLS_IN_CRAWL_QUEUE = 250
    MAX_URLS_IN_CRAWL_HISTORY = 30
    MAX_EMAILS_IN_EMAIL_QUEUE = 20
    MAX_EMAILS_INSERTED_AT_ONCE = 999

    def parse_settings():
        try:
            with open(Settings.SETTINGS_FILE, "r") as f:
                data = json.loads(f.read())
            Settings.OVERSEER_RUN_DELAY = data.get("overseer_run_delay")
            Settings.MAX_TIMEOUT = data.get("max_timeout")
            Settings.MIN_URLS_IN_WORKER_QUEUE = data.get("min_urls_in_worker_queue")
            Settings.MAX_URLS_IN_WORKER_QUEUE = data.get("max_urls_in_worker_queue")
            Settings.MAX_URLS_IN_CRAWL_QUEUE = data.get("max_urls_in_crawl_queue")
            Settings.MAX_URLS_IN_CRAWL_HISTORY = data.get("max_urls_in_crawl_history")
            Settings.MAX_EMAILS_IN_EMAIL_QUEUE = data.get("max_emails_in_email_queue")
            Settings.MAX_EMAILS_INSERTED_AT_ONCE = data.get("max_emails_inserted_at_once")
            return True
        except Exception as e:
            logging.critical(f"Failed to parse_settings: {e}")
            return False

    @staticmethod
    def save_settings():
        save_data = {
            "overseer_run_delay": Settings.OVERSEER_RUN_DELAY,
            "max_timeout": Settings.MAX_TIMEOUT,
            "min_urls_in_worker_queue": Settings.MIN_URLS_IN_WORKER_QUEUE,
            "max_urls_in_worker_queue": Settings.MAX_URLS_IN_WORKER_QUEUE,
            "max_urls_in_crawl_queue": Settings.MAX_URLS_IN_CRAWL_QUEUE,
            "max_urls_in_crawl_history": Settings.MAX_URLS_IN_CRAWL_HISTORY,
            "max_emails_in_email_queue": Settings.MAX_EMAILS_IN_EMAIL_QUEUE,
            "max_emails_inserted_at_once": Settings.MAX_EMAILS_INSERTED_AT_ONCE,
        }
        try:
            json_data = json.dumps(
                save_data, ensure_ascii=False, indent=4, sort_keys=True, default=str
            )
            with open(Settings.SETTINGS_FILE, "w") as save_file:
                save_file.write(json_data)

            return True
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            return False

    @staticmethod
    def update_setting(setting_name, value, save_changes=True):
        return_value = True

        match setting_name.upper():
            case "OVERSEER_RUN_DELAY":
                Settings.OVERSEER_RUN_DELAY = value
            case "MAX_TIMEOUT":
                Settings.MAX_TIMEOUT = value
            case "MIN_URLS_IN_WORKER_QUEUE":
                Settings.MIN_URLS_IN_WORKER_QUEUE = value
            case "MAX_URLS_IN_WORKER_QUEUE":
                Settings.MAX_URLS_IN_WORKER_QUEUE = value
            case "MAX_URLS_IN_CRAWL_QUEUE":
                Settings.MAX_URLS_IN_CRAWL_QUEUE = value
            case "MAX_URLS_IN_CRAWL_HISTORY":
                Settings.MAX_URLS_IN_CRAWL_HISTORY = value
            case "MAX_EMAILS_IN_EMAIL_QUEUE":
                Settings.MAX_EMAILS_IN_EMAIL_QUEUE = value
            case "MAX_EMAILS_INSERTED_AT_ONCE":
                Settings.MAX_EMAILS_INSERTED_AT_ONCE = value
            case _:
                return_value = False

        if save_changes:
            Settings.save_settings()

        return return_value
