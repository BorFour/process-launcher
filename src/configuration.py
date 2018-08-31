import json
import os
from collections import defaultdict

from .utils import get_config_folder

default_config_path = os.path.join(get_config_folder(), "configuration.json")

class Configuration(object):
    """docstring for Configuration"""
    def __init__(self, path=None):
        super(Configuration, self).__init__()
        self.path = path or default_config_path
        self._conf = defaultdict(lambda: None)

    def read(self):
        try:
            with open(self.path, 'r') as f:
                self._conf.update(json.load(f))
        except IOError:
            pass

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self._conf, f)

    def get(self, name):
        return self._conf[name]

    def set(self, name, value):
        self._conf[name] = value

    def store(self, name, value):
        self.set(name, value)
        self.write()
