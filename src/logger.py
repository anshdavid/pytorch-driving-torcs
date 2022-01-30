# -*- coding: utf-8 -*-
# https://docs.python.org/3/library/logging.html

import logging
import logging.config

logging.config.fileConfig(fname=r"./config/log.conf")
logger = logging.getLogger(__name__)
