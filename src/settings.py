import json
import logging
import os


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
    LOG_LEVEL = logging.DEBUG

    def parse_settings():
        if os.path.isfile(Settings.SETTINGS_FILE) is False:
            return

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
            Settings.LOG_LEVEL = data.get("log_level")
            logging.getLogger().setLevel(Settings.LOG_LEVEL)

            logging.info("Loaded settings successfully")
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
            "log_level": Settings.LOG_LEVEL,
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
            case "LOG_LEVEL":
                loglevel = Settings.translate_loglevel(value)
                Settings.LOG_LEVEL = loglevel
                logging.getLogger().setLevel(loglevel)
            case _:
                return_value = False

        if save_changes:
            Settings.save_settings()

        return return_value

    def translate_loglevel(log_level):
        if type(log_level) == int:
            if log_level == 10:
                return "DEBUG"
            elif log_level == 20:
                return "INFO"
            elif log_level == 30:
                return "WARNING"
            elif log_level == 40:
                return "ERROR"
            elif log_level == 50:
                return "CRITICAL"
            else:
                return "N/A"
        elif type(log_level) == str:
            log_level = log_level.upper()
            if log_level == "DEBUG":
                return logging.DEBUG
            elif log_level == "INFO":
                return logging.INFO
            elif log_level == "WARNING":
                return logging.WARNING
            elif log_level == "ERROR":
                return logging.ERROR
            elif log_level == "CRITICAL":
                return logging.CRITICAL
            else:
                return None
        else:
            return "type: N/A"
