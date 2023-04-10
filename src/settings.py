import json
import logging


# TODO: implement
class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.token = None
        self.discord_bot = None

    def parse_settings(self):
        try:
            with open(self.settings_file, "r") as f:
                data = json.loads(f.read())
            self.token = data.get("token")
            return True
        except Exception as e:
            logging.critical(f"Failed to parse_settings: {e}")
            return False
