from ccplatcfnginlibs.helpers.hooks import execute_hooks
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logger

import traceback
import sys

HOOK_LIST = [
    "ccplatcfnginlibs.hooks.post_destroy.clean_up_params",
    "ccplatcfnginlibs.hooks.custom_parameter_delete.hook",
]


def hook(provider, context, **kwargs):
    try:
        logger.info(f'Executing post-destroy hooks for module: {str(context.environment["module_name"])}')
        return execute_hooks(HOOK_LIST, provider, context, **kwargs)
    except BaseException as error:
        logger.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logger.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])