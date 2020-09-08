import os
from fake_useragent import UserAgent


class UAPool:
    def __init__(self):
        self.UAfilePath = os.getcwd() + '/fake_useragent.json'

    def get_header(self):
        ua = UserAgent(path=self.UAfilePath)
        return ua.random
