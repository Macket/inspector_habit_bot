import os
import json


class ConfigParser:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as infile:
            self.config = json.load(infile)

    def read(self, config_path):
        with open(config_path, 'r') as infile:
            self.config = json.load(infile)

    def get(self, section, var):
        return self.config.get(section).get(var)

    def get_section(self, section):
        return self.config.get(section)
