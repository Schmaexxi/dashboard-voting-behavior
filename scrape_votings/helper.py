from typing import Union, Dict, List
from urllib.request import urlopen, HTTPError, URLError
from json import dump
import sys
from socket import timeout
import logging
from literals import path_logging_file
from http.client import HTTPResponse


def try_open(url: str) -> HTTPResponse:
    """
    custom exception-endowed function for opening urls
    @params:
        url        - Required   : page to request
    """
    success: bool = False
    page: Union[HTTPResponse, None] = None
    while not success:
        try:
            page: HTTPResponse = urlopen(url)
            success = True
        except HTTPError as e:
            print("HTTPError code:  ", e.code)
        except URLError as e:
            print(e.reason)
        except timeout:
            print("Timeout - retrying")
    return page


# ensuring ascii encoding in json data
def json_dump(path: str, data: Dict[str, List[Union[Dict[str, Union[str, int]], int]]], **kwargs):
    with open(path, 'w+', encoding="utf-8") as outfile:
        dump(data, outfile, indent=4, ensure_ascii=False, **kwargs)


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress(iteration, total, prefix='',
                   suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of
        decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar,
                                            percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
    print()


# https://stackoverflow.com/questions/7621897/python-logging-module-globally
def setup_custom_logger(name: str) -> logging.Logger:
    formatter: logging.Formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                                     datefmt='%Y-%m-%d %H:%M:%S')
    handler: logging.FileHandler = logging.FileHandler(path_logging_file, mode='a')
    handler.setFormatter(formatter)
    # screen_handler = logging.StreamHandler(stream=sys.stdout)
    # screen_handler.setFormatter(formatter)
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # logger.addHandler(screen_handler)
    return logger
