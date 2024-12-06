import json


class ConfigManager:
    def __init__(self, config_file="./settings.json"):
        self.config_file = config_file
        self.config = self.read()

    def read(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def update(self, key, value):
        self.config[key] = value

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
