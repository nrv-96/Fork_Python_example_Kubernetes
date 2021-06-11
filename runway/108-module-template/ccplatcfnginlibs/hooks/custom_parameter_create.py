"""change endpoint security group"""
import yaml
from os import path
from ccplatcfnginlibs.helpers import ssm
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

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
        configs = {}
        if path.exists(module_config):
            with open(module_config) as file:
                configs = yaml.safe_load(file)
        if check_if_custom_parameters_exist(configs):
            for param in configs["customParameters"]:
                key = list(param)[0]
                value = param[key]
                description = "Custom Parameter"
                if len(value) >= 4096:
                    logging.info(
                        "ERROR: Parameter is longer than allowed 4096 characters truncating value"
                    )
                    value = value[:4095]
                    description = "TRUNCATED Custom Parameter"
                param_name = f"/ccplat/{namespace}/{module_name}/customParams/{key}"
                logging.info(f"Creating Parameter {param_name}")
                ssm.put_string_parameter(
                    name=param_name,
                    value=value,
                    description=description,
                    tagDict=context.tags,
                )
            return True
        else:
            logging.info("No parameters to create skipping")
            return True
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])