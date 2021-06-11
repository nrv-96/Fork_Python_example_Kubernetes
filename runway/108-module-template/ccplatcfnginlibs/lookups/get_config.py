"""Get configuration"""

from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import yaml
import traceback
import sys

TYPE_NAME = 'configs'

class Lookup(LookupHandler):

    @classmethod
    def handle(cls, value, context: Context, provider: BaseProvider, **kwargs) -> str: # pragma: no cover
        """
        Get configuration based on inputs
        Example:
            ex. object
                vStructuredConfig:
                    desiredVar: someValue
            ex. lookup
                configs: libs.lookups.get_config.handle
            ex. usage
                ${configs ${module_config} vStructuredConfig desiredVar}
        """
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            # split passed in values
            values = [x.strip() for x in value.split(" ")]

            config_file = values[0]
            structured_config = values[1]
            desired_var = values[2]

            with open(config_file) as stream:
                config = yaml.safe_load(stream)

            return config[structured_config][desired_var]
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup

def handle(value, context, provider): # pragma: no cover
    """
    Get configuration based on inputs
    Example:
        ex. object
            vStructuredConfig:
                desiredVar: someValue
        ex. lookup
            configs: libs.lookups.get_config.handle
        ex. usage
            ${configs ${module_config} vStructuredConfig desiredVar}
    """
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        # split passed in values
        values = [x.strip() for x in value.split(" ")]

        config_file = values[0]
        structured_config = values[1]
        desired_var = values[2]

        with open(config_file) as stream:
            config = yaml.safe_load(stream)

        return config[structured_config][desired_var]
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])