import requests


class Channel:

    def __init__(self, config):
        self.end_point = config["endpoint"]
        self.channel = config["channel"]
        self.token = config["token"]
        self.message = ""
        self.generate()

    def generate(self, message=""):
        if message != "":
            pass
        else:
            self.end_point = self.end_point.replace("{TOKEN}", self.token)

    def clean(self, message):
        return message.replace(" ", SpecialChar.empty)

    def send_message(self, message):
        try:
            self.message = message
            self.generate(self.message)
            headers = {"Content-Type": "application/json"}
            payload = {
                "chat_id": self.channel,
                "text": self.message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            requests.post(self.end_point, json=payload, headers=headers)
            return True
        except Exception:
            return False


class SpecialChar:
    empty = "%20"
