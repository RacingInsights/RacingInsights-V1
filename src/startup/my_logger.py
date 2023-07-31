"""Module for logging"""
import logging

from os import makedirs

LOGS_FOLDER_NAME = 'logs'
LOGS_FILE_NAME = f'{LOGS_FOLDER_NAME}/RI_logs.log'


def initialize_logging(production: bool = False) -> None:
    """Sets all the settings/folders for application logging"""
    if production:
        file_name = LOGS_FILE_NAME
    else:
        file_name = None

    # If logs directory doesn't exist, make one
    makedirs(LOGS_FOLDER_NAME, exist_ok=True)

    logging.basicConfig(format='|%(asctime)s | %(levelname)s | %(message)s\n'
                               '|---------------------------| %(pathname)s:%(lineno)d ',
                        filename=file_name,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
