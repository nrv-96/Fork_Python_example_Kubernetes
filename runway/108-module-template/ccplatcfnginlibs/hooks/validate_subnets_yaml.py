"""Validate subnets found in a yaml file"""
import yaml
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER
import traceback
import sys

def validate_subnets(provider, context, **kwargs):
    """
    Validate subnets
    Parameters:
        allowed_subnets (optional): allowable subnets
        yaml_file (required): yaml file containing information about subnets used
        object (required): the object containing the subnets
        key (required): the name of the key which points to the value of the subnets
        max_subnets (optional): maximum number of subnets used
    Returns:
        Validator Response
    """
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        return_value = ValidatorResponse(None, None)

        # validate required arguments
        if "yaml_file" not in kwargs:
            return_value.response = False
            return_value.message = "Missing required argument 'yaml_file'"
            return return_value
        if "object" not in kwargs:
            return_value.response = False
            return_value.message = "Missing required argument 'object'"
            return return_value
        if "key" not in kwargs:
            return_value.response = False
            return_value.message = "Missing required argument 'key'"
            return return_value

        allowed_subnets = set(kwargs.get("allowed_subnets", []))
        subnets = get_subnets_from_yaml(kwargs["yaml_file"], kwargs["object"],kwargs["key"])
        max_subnets = kwargs.get("max_subnets", None)
        if max_subnets is not None:
            max_subnets = int(max_subnets)

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

def get_subnets_from_yaml(yaml_file, obj, key):
    """look up subnet information from yaml file"""
    with open(yaml_file) as stream:
        config = yaml.safe_load(stream)
    print(yaml_file)
    print(config)
    print(config[obj])
    return config[obj][key].split(",")


class ValidatorResponse:
    def __init__(self, response, message):
        self.response = response
        self.message = message

    def __str__(self):
        return "{}, {}".format(self.response, self.message)

    def __bool__(self):
        return self.response