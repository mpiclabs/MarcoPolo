import logging
import os
import sys
from marcopolo.paths import paths

# Configure the format for log messages
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(log_format)

# General logger-- this traces all events that happen in order, so you can easily trace
general_logger = logging.getLogger('general_logger')
general_logger.setLevel(logging.DEBUG)  # Use DEBUG to capture all log levels
general_handler_file = logging.FileHandler(f'{paths.LOGS}/general.log')
general_handler_file.setLevel(logging.DEBUG)
general_handler_file.setFormatter(log_format)
general_logger.addHandler(general_handler_file)  # General captures everything
general_logger.addHandler(stdout_handler)  # General captures everything

# Summary logger-- this logs a summary of each attack that occurs
summary_logger = logging.getLogger('summary_logger')
summary_logger.setLevel(logging.DEBUG)  # Use DEBUG to capture all log levels
summary_handler = logging.FileHandler(paths.LOGS / 'summary.log')
summary_handler.setLevel(logging.DEBUG)
summary_handler.setFormatter(log_format)
summary_logger.addHandler(summary_handler)  # Summary captures everything
summary_logger.addHandler(stdout_handler)  # Summary also goes to stdout

# Error logger-- this only includes things that went wrong and need to come to attention
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.DEBUG)
error_handler = logging.FileHandler(f'{paths.LOGS}/errors.log')
error_handler.setLevel(logging.DEBUG)
error_handler.setFormatter(log_format)
error_logger.addHandler(error_handler)
error_logger.addHandler(stdout_handler)  # Errors also go to general.log
error_logger.addHandler(general_handler_file)  # Errors also go to stdout

# HTTP Logger-- all HTTP communications
http_logger = logging.getLogger('http_logger')
http_logger.setLevel(logging.DEBUG)
http_handler = logging.FileHandler(f'{paths.LOGS}/http.log')
http_handler.setLevel(logging.DEBUG)
http_handler.setFormatter(log_format)
http_logger.addHandler(http_handler)
#http_logger.addHandler(general_handler_file)  # HTTP logs also go to stdout



def clear_log_files() -> None:
    log_files = paths.LOGS.glob('*.log')
    for log_file in log_files:
        with open(log_file, 'w'):
            pass  # Opening with 'w' truncates the file
        general_logger.debug(f"{log_file} cleared")
