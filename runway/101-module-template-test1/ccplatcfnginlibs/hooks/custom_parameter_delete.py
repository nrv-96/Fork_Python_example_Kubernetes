"""change endpoint security group"""

import os
import boto3
import sys  # pragma: no cover
import yaml
import traceback
from os import path
from ccplatcfnginlibs.helpers import ssm

sys.path.append("../")  # pragma: no cover
from ccplatcfnginlibs.helpers import cloudformation  # pragma: no cover
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging


def check_if_custom_parameters_exist(configs):
    for config in configs:
        if config == "customParameters":
            return True
    logging.info("No Custom Parameters Found")
    return False


def hook(provider, context, **kwargs):  # pragma: no cover
    """Change security group for S3SFTP endpoint"""
    try:
        logging.info(f'Running hook for module: {str(context.environment["module_name"])}')
        namespace = context.namespace
        module_name = str(context.environment["module_name"])
        module_config = context.environment["module_config"]
        parameters = []
        configs = {}
        if path.exists(module_config):
            with open(module_config) as file:
                configs = yaml.safe_load(file)
        if check_if_custom_parameters_exist(configs):
            for param in configs["customParameters"]:
                key = list(param)[0]
                param_name = f"/ccplat/{namespace}/{module_name}/customParams/{key}"
                parameters.append(param_name)
            logging.info(f"Deleting Parameters {parameters}")
            ssm.delete_parameters(parameters)
            return True
        else:
            logging.info("No parameters to delete skipping")
            return True
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])