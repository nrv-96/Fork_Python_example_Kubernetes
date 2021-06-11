#!/usr/bin/env python
from ccplatcfnginlibs.helpers import ssm
import yaml
import traceback
import sys
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

"""Post Destroy Hooks"""


def clean_up_params(provider, context, **kwargs):
    """deletes all parameters published by stacker to ssm"""
    try:
        namespace = context.namespace
        module_name = str(context.environment["module_name"])
        LOGGER.info(f'Running hook for module: {module_name}')
        stack_postfix = context.environment.get("stack_postfix")
        if stack_postfix:
            module_name = f"{module_name}/{stack_postfix}"

        parameters = ssm.get_module_parameters(f"/ccplat/{namespace}/{module_name}")
        params_to_delete = []
        for param in parameters:
            params_to_delete.append(param["Name"])
        ssm.delete_parameters(params_to_delete)
        return True
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])