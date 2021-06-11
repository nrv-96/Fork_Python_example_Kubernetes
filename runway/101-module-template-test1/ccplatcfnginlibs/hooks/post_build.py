#!/usr/bin/env python
from ccplatcfnginlibs.helpers import ssm, cloudformation
from os import path
import traceback
import sys
import yaml
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

"""Post Deployment Hooks"""

warning_message = "*** This param value has been truncated to fit within the maximum length for ssm standard params. *** "


def publish_params(provider, context, **kwargs):
    """Publish all parameters passed into stacker to SSM"""
    try:
        namespace = context.namespace
        module_name = str(context.environment["module_name"])
        LOGGER.info(f'Running hook for module: {module_name}')
        stack_postfix = context.environment.get("stack_postfix")
        if stack_postfix:
            module_name = f"{module_name}/{stack_postfix}"

        truncate_config_if_needed = True
        if "truncate_config_if_needed" in kwargs:
            if (
                isinstance(kwargs["truncate_config_if_needed"], str)
                and kwargs["truncate_config_if_needed"].lower() == "false"
            ):
                truncate_config_if_needed = False
            else:
                truncate_config_if_needed = bool(kwargs["truncate_config_if_needed"])

        for param in context.environment:
            param_name = f"/ccplat/{namespace}/{module_name}/params/{param}"
            if param != "module_config":
                ssm.put_string_parameter(
                    name=param_name,
                    value=str(context.environment[param]),
                    description="stacker environment",
                    tagDict=context.tags,
                )

        if "module_config" in context.environment and path.exists(
            context.environment["module_config"]
        ):
            with open(context.environment["module_config"], "r") as file:
                module_config_dict = yaml.full_load(file)
                for item, doc in module_config_dict.items():
                    module_config_string = str(module_config_dict)
                    param_description = "stacker environment"
                    if truncate_config_if_needed:
                        module_config_string = check_length_and_truncate_if_needed(
                            module_config_string
                        )
                        if module_config_string.startswith(warning_message):
                            param_description = param_description + " (TRUNCATED)"
                    param_name = f"/ccplat/{namespace}/{module_name}/params/module_config"
                    ssm.put_string_parameter(
                        name=param_name,
                        value=module_config_string,
                        description=param_description,
                        tagDict=context.tags,
                    )

        for stack in context.config.stacks:
            stack_name = stack.name
            if stack.stack_name and stack.stack_name is not stack.name:
                stack_name = stack.stack_name
            outputs = cloudformation.get_all_outputs(f"{namespace}-{stack_name}")
            for output in outputs:
                param_name = (
                    f"/ccplat/{namespace}/{module_name}/{stack_name}/{output['OutputKey']}"
                )
                ssm.put_string_parameter(
                    name=param_name,
                    value=output["OutputValue"],
                    description="Cloduformation Output",
                    tagDict=context.tags,
                )

        return True
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

def check_length_and_truncate_if_needed(value):
    ssm_param_max_length = 4096
    if len(value) > ssm_param_max_length:
        return warning_message + value[0 : ssm_param_max_length - len(warning_message)]
    else:
        return value
