'''Testing lambdas'''

import logging

LOG_LEVEL = 'INFO'

LOGGER = logging.getLogger()
LOGGER.setLevel(LOG_LEVEL)

def lambda_handler(event, context):
    ''' lambda handler '''
    LOGGER.info('Hello')
    return True
