import yaml
import sys
import os

def load_yaml(filename):
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="UTF-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data
    return None


class ConfigManager(object):
    def __init__(self, config_path):

        self.config_dict = load_yaml(config_path)

    def get_config(self, key: str, defaultVal):
        if key in self.config_dict and self.config_dict[key] is not None:
            return self.config_dict[key]

        for k, v in self.config_dict.items():
            if k == key and v is not None:
                return v

            if type(v) is dict:
                for k_, v_ in v.items():
                    if k_ == key and v_ is not None:
                        return v_
        return defaultVal

    def get_var_config(self, key: str, defaultVal):
        if key in self.var_config_dict:
            return self.var_config_dict[key]

        for k, v in self.var_config_dict.items():
            if k == key:
                return v

            if type(v) is dict:
                for k_, v_ in v.items():
                    if k_ == key:
                        return v_
        return defaultVal


g_config = ConfigManager('./config.yaml')


