#!/usr/bin/env python

from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

"""Lookup Log Setting"""

from ccplatcfnginlibs.helpers import cloudwatch  # pragma: no cover
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

TYPE_NAME = "cloudwatch"


class Lookup(LookupHandler):
    @classmethod
    def handle(cls, value, context: Context, provider: BaseProvider, **kwargs) -> str:
        """get CW retention setting"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            env = context.environment.get("environment")

            try:
                retention_days = cloudwatch.get_log_retention_setting(env)
            except:
                raise Exception("Log retention setting not found")

            return retention_days
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup


def lookup_log_retention_setting(context, **kwargs):
    """get CW retention setting"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        env = context.environment.get("environment")

        try:
            retention_days = cloudwatch.get_log_retention_setting(env)
        except:
            raise Exception("Log retention setting not found")

        return retention_days
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])