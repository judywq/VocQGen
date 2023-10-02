import datetime
import json
import os
from setting import DEFAULT_LOG_LEVEL, RANDOM_SEED

import logging
logger = logging.getLogger(__name__)


class ExtendableDict(dict):
    def extend(self, key, value: set):
        if key not in self.keys():
            self[key] = set()
        self[key].update(value)
    
    def merge(self, other: dict):
        for key, value in other.items():
            if key not in self.keys():
                self[key] = set()
            self[key].update(value)
            

def setup_log(level=None, log_path='./log/txt'):
    if not level:
        level = logging.getLevelName(DEFAULT_LOG_LEVEL)
    if not os.path.exists(log_path):
        os.makedirs(log_path)    
        
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    filename = get_date_str()
    file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, filename))
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(level=level)

    # https://stackoverflow.com/a/11111212
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[file_handler, console_handler])


def cloze_sentence(sentence, word):
    """Replace the word in the sentence with a blank (4 underscores)
    """
    return sentence.replace(word, '_' * 4)


def fill_cloze(sentence, word):
    """Fill the blank in the sentence with the word
    """
    return sentence.replace('_' * 4, word)


def get_date_str():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def setup_randomness():
    if RANDOM_SEED > 0:
        import random
        random.seed(RANDOM_SEED)


def load_config(file='./config.json'):
    if not os.path.exists(file):
        logger.error(f"Config file does not exist: {file}")
        exit(-1)

    with open(file, 'r') as f:
        config = json.load(f)
    return config
