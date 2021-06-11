"""Dictionary of Key/Value Stack Outputs"""

import yaml
from ccplatcfnginlibs.helpers import cloudformation  # pragma: no cover
from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

TYPE_NAME = "getStackOutputs"


class Lookup(LookupHandler):
    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> dict:  # pragma: no cover
        """stack outputs for a given stack"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            stack_name = value.strip()
            namespace = str(context.environment.get("namespace"))
            full_stack_name = f"{namespace}-{stack_name}"

            stack_outputs = cls.get_all_stack_outputs(full_stack_name)
            return stack_outputs
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])
            
    @classmethod
    def get_all_stack_outputs(cls, full_stack_name) -> dict:
        """get stack outputs for the given stack"""
        stack_outputs = {}
        all_outputs = cloudformation.get_all_outputs(full_stack_name)

        for output in all_outputs:
            stack_outputs[output["OutputKey"]] = output["OutputValue"]

        return stack_outputs
