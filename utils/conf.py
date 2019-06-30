import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigParser:
    def __init__(self, config_file='config.json'):
        with open(os.path.join(BASE_DIR, config_file), 'r') as infile:
            self.config = json.load(infile)

    def read(self, config_file):
        with open(os.path.join(BASE_DIR, config_file), 'r') as infile:
            self.config = json.load(infile)

    def get(self, section, var):
        return self.config.get(section).get(var)

    def get_section(self, section):
        return self.config.get(section)
