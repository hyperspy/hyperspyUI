# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import logging


def init_logging(level=logging.INFO):
    """Sets up logging.

    Sets the log level for all loggers to `level`,
    unless `level` is given as `None`.
    """
    logging.basicConfig(level=level)
    logging.captureWarnings(True)


def set_hyperspyui_log_level(level, set_main=True):
    """Set a log level for HyperSpyUI loggers"""
    logger.setLevel(level)
    if set_main:
        _baseLogger = logging.getLogger()
        _baseLogger.setLevel(level)


logger = logging.getLogger('hyperspyui')

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
exception = logger.exception
critical = logger.critical
