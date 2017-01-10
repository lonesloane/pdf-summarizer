import ConfigParser
import logging

# Get configuration parameters
_config = ConfigParser.SafeConfigParser()
_config.read('config/pdfsummarizer.conf')

# Set appropriate logging level
logging_level = getattr(logging, _config.get('LOGGING', 'level').upper(), None)
if not isinstance(logging_level, int):
    raise ValueError('Invalid log level: %s' % _config.get('LOGGING', 'level'))
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)
_log_level = 1  # verbosity of log. 1:debug - 2:verbose - 3:visual

logger.info('Logging object initialized with log level {level}'.format(level=_log_level))
