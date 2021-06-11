from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

def hook(provider, context, **kwargs):  # pragma: no cover
    try:
        logging.info(f'Running hook for module: {str(context.environment["module_name"])}')
        stack_postfix = context.environment.get("stack_postfix")
        logging.debug(f"stack_postfix: {stack_postfix}")
        if stack_postfix:
            for stack in context.config.stacks:
                stack.stack_name = f"{stack.name}-{stack_postfix}"
                logging.debug(f"stack_name: {stack.stack_name}")

        return True
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])