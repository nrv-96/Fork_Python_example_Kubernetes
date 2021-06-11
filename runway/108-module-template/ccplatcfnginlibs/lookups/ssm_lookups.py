#!/usr/bin/env python
""" return ssm parameter dictionary """
from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

from ccplatcfnginlibs.helpers import ssm
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

TYPE_NAME = "ssm_lookups"


class Lookup(LookupHandler):
    """ lookup ssm parameters """

    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=unused-argument
        """ handle the lookup """
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            values = [x.strip() for x in value.split(" ")]

            key = values[0]
            param = values[1]

            parameter_dict = eval(ssm.get_parameter(key))

            return parameter_dict[param]
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def dict_lookup(value, context, provider):  # pylint: disable=W0613
    """ handle the lookup """
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        values = [x.strip() for x in value.split(" ")]

        key = values[0]
        param = values[1]

        parameter_dict = eval(ssm.get_parameter(key))

        return parameter_dict[param]
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])