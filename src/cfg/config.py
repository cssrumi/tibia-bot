import os
import sys


def get_config_path() -> str:
    try:
        config_path = sys.argv[1]
    except IndexError:
        config_path = None
    if not config_path or not os.path.exists(config_path):
        raise RuntimeError("Invalid path to config. Please supply valid config path as an argument")
    return config_path
