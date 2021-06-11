from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

import traceback
import sys

def validate_subnets(provider, context, **kwargs):
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        allowed_subnets = set(kwargs.get("allowed_subnets", []))
        subnets = set([] if not kwargs.get("subnets", False) else kwargs.get("subnets").split(","))
        max_subnets = kwargs.get("max_subnets", None)
        if max_subnets is not None:
            max_subnets = int(max_subnets)

        return_value = ValidatorResponse(None, None)

        if max_subnets and len(subnets) > max_subnets:
            return_value.response = False
            return_value.message = "The subnets provided which are '{}' must be only '{}' of '{}'"
            return_value.message = return_value.message.format(subnets, max_subnets, allowed_subnets)
        elif not allowed_subnets or not subnets:
            return_value.message = "Missing required args allowed_subnets : '{}' and subnets : '{}'".format(
                allowed_subnets, subnets)
            return_value.response = False
        else:
            return_value.message = "The subnets which is '{}' must be a subset of '{}'"
            return_value.message = return_value.message.format(subnets, allowed_subnets)
            return_value.response = allowed_subnets.issuperset(subnets)

        return return_value
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

class ValidatorResponse:
    def __init__(self, response, message):
        self.response = response
        self.message = message

    def __str__(self):
        return "{}, {}".format(self.response, self.message)

    def __bool__(self):
        return self.response