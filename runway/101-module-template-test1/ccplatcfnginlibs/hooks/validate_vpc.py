#!/usr/bin/env python
"""Validate VPC Exists and validate version"""
import semver
from ccplatcfnginlibs.helpers.ssm import get_parameter
from ccplatcfnginlibs.helpers.utils import test_dict_for_bool
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

import traceback
import sys

def checkKey(dict, key):
    """
    checks if key exists in dictonary
    """
    if key in dict.keys():
        return True
    else:
        return False


def validate_vpc(provider, context, **kwargs):
    """
    Checks that the vpc module is deployed, and that its major version is correct
    """
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        if test_dict_for_bool("validateVpc", kwargs):
            expected_major_version = context.environment["vpc_module_major_version"]
            if checkKey(context.environment, "networking_tier_namespace"):
                networking_namespace = context.environment["networking_tier_namespace"]
            else:
                networking_namespace = context.namespace
            LOGGER.info(f"Expected Major Version: {expected_major_version}")
            LOGGER.info(f"Networking Namespace: {networking_namespace}")
            if networking_namespace == "":
                networking_namespace = context.namespace
            parameter = f"/ccplat/{networking_namespace}/cloud-common-vpc-module/params/module_version"
            try:
                vpc_version = get_parameter(parameter)
                LOGGER.info(f"Parameter Store Version: {vpc_version}")
            except Exception as e:
                LOGGER.error(f"VPC NOT FOUND")
                LOGGER.error(f"Exception occured: {e}")
                return False
            if vpc_version == "local":
                LOGGER.info("VPC running in local version")
                return True
            else:
                vpc_version = semver.VersionInfo.parse(vpc_version)
                LOGGER.info(vpc_version.major)
            if int(vpc_version.major) == int(expected_major_version):
                LOGGER.info("VPC Found")
                return True
            else:
                LOGGER.error("VPC Module Version Deployed Does not match expected version")
                return False
        else:
            LOGGER.info("Skipping VPC validation")
            return True
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])