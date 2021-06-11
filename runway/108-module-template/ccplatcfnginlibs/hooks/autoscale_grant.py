""" Creates role and grant needed to allow EKS to launch encrypted EKS AMIs """
import time

import sys
import traceback
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

sys.path.append("../")

from ccplatcfnginlibs.helpers import iam, kms  # pylint: disable=no-name-in-module

KMS_KEYS = {
    "us-east-1": "arn:aws:kms:us-east-1:602788979237:key/2cdd488f-89b6-416e-9a30-a03708d1d3df",
    "us-west-2": "arn:aws:kms:us-west-2:602788979237:key/6962dfad-19da-4e78-810b-9df72326f793",
}

SLEEP = 15


def hook(provider, context, **kwargs):  # pylint: disable=unused-argument
    """ Hook called by stacker """
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')

        resp = True
        region = context.environment.get("region")
        kms_key_id = KMS_KEYS[region]

        role_arn = iam.create_autoscaling_service_role(region)
        if role_arn is not None:
            time.sleep(SLEEP)  # allow role creation to finish if new
            grant_exists = kms.grant_exists_for_role(kms_key_id, role_arn, region)
            if not grant_exists:
                resp = kms.create_grant(kms_key_id, role_arn, region)
        else:
            resp = False
        return resp
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])