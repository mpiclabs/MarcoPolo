import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
# Configure the format for log messages
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Summary logger-- this logs a summary of each attack that occurs
summary_logger = logging.getLogger('summary_logger')
summary_logger.setLevel(logging.DEBUG)  # Use DEBUG to capture all log levels
summary_handler = logging.FileHandler(f'{dir_path}/../results/summary.log')
summary_handler.setLevel(logging.DEBUG)
summary_handler.setFormatter(log_format)
summary_logger.addHandler(summary_handler)  # Summary captures everything

# General logger-- this traces all events that happen in order, so you can easily trace
general_logger = logging.getLogger('general_logger')
general_logger.setLevel(logging.DEBUG)  # Use DEBUG to capture all log levels
general_handler = logging.FileHandler(f'{dir_path}/../results/general.log')
general_handler.setLevel(logging.DEBUG)
general_handler.setFormatter(log_format)
general_logger.addHandler(general_handler)  # General captures everything

# Error logger-- this only includes things that went wrong and need to come to attention
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.DEBUG)
error_handler = logging.FileHandler(f'{dir_path}/../results/errors.log')
error_handler.setLevel(logging.DEBUG)
error_handler.setFormatter(log_format)
error_logger.addHandler(error_handler)
error_logger.addHandler(general_handler)  # Errors also go to general.log

# HTTP Logger-- all HTTP communications
http_logger = logging.getLogger('http_logger')
http_logger.setLevel(logging.DEBUG)
http_handler = logging.FileHandler(f'{dir_path}/../results/http.log')
http_handler.setLevel(logging.DEBUG)
http_handler.setFormatter(log_format)
http_logger.addHandler(http_handler)
http_logger.addHandler(general_handler)  # HTTP logs also go to general.log