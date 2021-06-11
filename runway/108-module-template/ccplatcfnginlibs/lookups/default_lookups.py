"""Determine VPC and subnets based on configuration"""

from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

import boto3
import yaml
import os
import traceback
import sys

from ccplatcfnginlibs.helpers import cloudformation  # pragma: no cover
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging


class Lookup(LookupHandler):
    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pragma: no cover
        """
        returns cfn output or defaults based on output
        :return:
        """
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            values = [x.strip() for x in value.split(" ")]
            stack = values[0]
            output = values[1]
            default = values[2]
            try:
                return cloudformation.get_output(
                    context.environment["namespace"] + "-" + stack, output
                )
            except Exception as e:
                logging.debug(e)
                logging.info("Defaulting to default variable")
                return default
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup


def default_cfn_lookup(value, context, provider):
    """
    returns cfn output or defaults based on output
    :return:
    """
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        values = [x.strip() for x in value.split(" ")]
        stack = values[0]
        output = values[1]
        default = values[2]
        try:
            return cloudformation.get_output(
                context.environment["namespace"] + "-" + stack, output
            )
        except Exception as e:
            logging.debug(e)
            logging.info("Defaulting to default variable")
            return default
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])