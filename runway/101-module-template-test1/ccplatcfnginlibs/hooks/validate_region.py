#!/usr/bin/env python
from os import environ
import traceback
import sys
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER
"""Validate Region"""

def hook(provider, context, **kwargs):
    """validate context region with aws default region"""
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        if 'region' not in context.environment:
            return True
        elif 'AWS_DEFAULT_REGION' not in environ:
            environ['AWS_DEFAULT_REGION'] = context.environment['region']
            return True
        else:
            return context.environment['region'] == environ.get('AWS_DEFAULT_REGION')
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])