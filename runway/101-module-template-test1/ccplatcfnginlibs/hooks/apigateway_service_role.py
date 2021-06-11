""" Creates role and grant needed to allow API Gateway """

import sys
import traceback
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

sys.path.append("../")

from ccplatcfnginlibs.helpers import iam  # pylint: disable=no-name-in-module

def hook(provider, context, **kwargs):  # pylint: disable=unused-argument
    """ Hook called by stacker """
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        region = context.environment.get("region")

        return iam.create_api_gateway_service_role(region)
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])