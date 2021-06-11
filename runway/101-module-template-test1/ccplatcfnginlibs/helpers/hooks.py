import importlib
import sys
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logger


def execute_hooks(hook_list, provider, context, **kwargs):
    successful = True
    for hook_path in hook_list:
        logger.info(f"Executing hook {hook_path}")
        try:
            method = load_method_from_path(hook_path)
            successful = method(context=context, provider=provider, **kwargs)
            if not successful:
                logger.error(f"Hook {hook_path} returned a False response")
        except Exception as exception:
            logger.error(f"Error occurred while calling hook {hook_path}: {exception}")
            successful = False
        if not successful:
            break

    return successful


def load_method_from_path(hook_path):
    module_path, object_name = hook_path.rsplit(".", 1)
    importlib.import_module(module_path)
    return getattr(sys.modules[module_path], object_name)
