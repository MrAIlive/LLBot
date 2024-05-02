# -*- coding:utf-8 -*-  -->  Python = "优雅"

"""
This is a log module!
Usage type is :
from OntBot.log import logger
"""
import logging
import os
import sys
import colorlog

__all__ = [
    "logger"
]
None if os.path.exists(".\\data\\Log") else os.makedirs(".\\data\\Log")
#  格式
log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red'
}
formatter = logging.Formatter("[%(asctime)s %(name)s][%(levelname)s] %(filename)s 第%(lineno)d行 %(message)s",
                              datefmt="%Y年%M月%d日%H时%M分%S秒")
console_formatter = colorlog.ColoredFormatter(
    "[%(asctime)s %(name)s]%(log_color)s[%(levelname)s] %(message)s",
    datefmt="%Y年%M月%d日%H时%M分%S秒", log_colors=log_colors_config, no_color=False)

logger = logging.getLogger('LLBot')
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(filename=".\\data\\Log\\LLBot.log",mode="w+", encoding='utf-8')
fileHandler.setLevel(logging.INFO)

consoleHandler.setFormatter(console_formatter)
fileHandler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

consoleHandler.close()
fileHandler.close()
