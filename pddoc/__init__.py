# coding=utf-8

import logging
from colorformatter import ColorizingStreamHandler

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(ColorizingStreamHandler())
