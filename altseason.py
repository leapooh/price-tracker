import subprocess
import time
from bs4 import BeautifulSoup
import os
import re


class AltSeason:
    def __init__(self, url):
        self.url = url
        self.content = None

    def get_current_index(self):
        try:
            return self.__fetch_and_process_content()
        except subprocess.CalledProcessError as e:
            print(f"The curl command failed with error: {e}")
            return None, None
        except FileNotFoundError as e:
            print(f"The file was not found: {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None

    def __fetch_and_process_content(self):
        self.content = self.__fetch_content()
        if self.content:
            index = self.__process_content(self.content)
            percentage = self.__process_percentage(self.content)
            return index, percentage
        return None, None

    def __fetch_content(self):
        command = ["curl", "-s", self.url, "-o", "/tmp/altseason.html"]
        subprocess.run(command, check=True)
        time.sleep(1)
        with open("/tmp/altseason.html", "r", encoding="utf-8") as file:
            return file.read()

    def __process_content(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        button = soup.find('button', class_='nav-link timeselect active', id='home-tab', attrs={
            'data-bs-toggle': 'tab',
            'data-bs-target': '#season',
            'type': 'button',
            'role': 'tab',
            'aria-controls': 'season',
            'aria-selected': 'true'
        })
        if button:
            b_tag = button.find('b')
            if b_tag:
                return b_tag.string.strip('() %')
        return None

    def __process_percentage(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        percentage_paragraph = soup.find('p', class_='bccblock')
        if percentage_paragraph:
            percentage_match = re.search(r'(\d+)% of the.*?performed better than Bitcoin', percentage_paragraph.text)
            if percentage_match:
                return percentage_match.group(1).strip('%')
        return None

    def __del__(self):
        try:
            os.remove("/tmp/altseason.html")
        except OSError:
            pass