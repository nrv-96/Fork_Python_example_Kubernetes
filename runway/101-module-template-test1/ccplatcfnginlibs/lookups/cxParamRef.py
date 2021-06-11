"""Determine SSM Param lookup based on the custom namespace, if provided"""

from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

import boto3
from ccplatcfnginlibs.helpers import ssm  # pragma: no cover
from ccplatcfnginlibs.helpers import cloudformation  # pragma: no cover
from botocore.exceptions import ClientError
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

import traceback
import sys

TYPE_NAME = "cxParamRef"


class Lookup(LookupHandler):
    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pragma: no cover
        """Cross namespace param lookup"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            # split passed in values
            values = [x.strip() for x in value.split(" ")]
            default_value = ""

            cls.validate(values)

            stack_resource_name = str(values[0])
            stack_name, param_name = cls.deconstruct(str(values[1]))
            custom_namespace = str(values[2])

            namespace = cls.determine_namespace(context, custom_namespace)

            if len(values) > 3:
                default_value = str(values[3])

            result = None
            try:
                result = ssm.get_stack_parameter(
                    stack_resource_name, stack_name, param_name, namespace
                )
                logging.info(f"{param_name} found: {result}")
            except ClientError as err:
                if err.response["Error"]["Code"] == "ParameterNotFound":
                    logging.error(
                        "Parameter '%s' in namespace '%s' not found"
                        % (param_name, namespace)
                    )
                else:
                    logging.error(
                        "Unexpected error occurred looking for Parameter '%s' in namespace '%s': %s"
                        % (param_name, namespace, err)
                    )
            except Exception as exp:
                logging.error(
                    "Unexpected error occurred looking for Parameter '%s' in namespace '%s': %s"
                    % (param_name, namespace, exp)
                )

            if not result:
                if default_value:
                    logging.info(
                        f"Param not found in SSM, using default value: {default_value}"
                    )
                    result = default_value
                else:
                    logging.info("Param not found in SSM. No default value provided.")
                    raise Exception(
                        f"Param: {param_name} not found in SSM. No default value provided."
                    )

            return result
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

    @classmethod
    def determine_namespace(cls, context, custom_namespace):
        if custom_namespace in context.environment:
            namespace = str(context.environment.get(custom_namespace))
            logging.info(f"Using custom namespace: {namespace}")
        else:
            namespace = str(context.environment.get("namespace"))
            logging.info(f"Using default namespace: {namespace}")

        return namespace

    @classmethod
    def validate(cls, values):
        """Validates the values"""
        if len(values) < 3:
            raise Exception(
                "Insufficient number of arguments provided. Required: 3+, Supplied: "
                + str(len(values))
            )

    @classmethod
    def deconstruct(cls, value):
        """Deconstruct the value."""
        try:
            stack_name, param_name = value.split("::")
        except ValueError:
            raise ValueError(
                "output handler requires syntax "
                "of <stack>::<param_name>.  Got: %s" % value
            )

        return stack_name, param_name


## Remove old lookup


def handle(value, context, provider):  # pragma: no cover
    """Cross namespace param lookup"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        # split passed in values
        values = [x.strip() for x in value.split(" ")]
        default_value = ""

        validate(values)

        stack_resource_name = str(values[0])
        stack_name, param_name = deconstruct(str(values[1]))
        custom_namespace = str(values[2])

        namespace = determine_namespace(context, custom_namespace)

        if len(values) > 3:
            default_value = str(values[3])

        result = None
        try:
            result = ssm.get_stack_parameter(
                stack_resource_name, stack_name, param_name, namespace
            )
            logging.info(f"{param_name} found: {result}")
        except ClientError as err:
            if err.response["Error"]["Code"] == "ParameterNotFound":
                logging.error(
                    "Parameter '%s' in namespace '%s' not found" % (param_name, namespace)
                )
            else:
                logging.error(
                    "Unexpected error occurred looking for Parameter '%s' in namespace '%s': %s"
                    % (param_name, namespace, err)
                )
        except Exception as exp:
            logging.error(
                "Unexpected error occurred looking for Parameter '%s' in namespace '%s': %s"
                % (param_name, namespace, exp)
            )

        if not result:
            if default_value:
                logging.info(
                    f"Param not found in SSM, using default value: {default_value}"
                )
                result = default_value
            else:
                logging.info("Param not found in SSM. No default value provided.")
                raise Exception(
                    f"Param: {param_name} not found in SSM. No default value provided."
                )

        return result
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

def determine_namespace(context, custom_namespace):
    if custom_namespace in context.environment:
        namespace = str(context.environment.get(custom_namespace))
        logging.info(f"Using custom namespace: {namespace}")
    else:
        namespace = str(context.environment.get("namespace"))
        logging.info(f"Using default namespace: {namespace}")

    return namespace


def validate(values):
    """Validates the values"""
    if len(values) < 3:
        raise Exception(
            "Insufficient number of arguments provided. Required: 3+, Supplied: "
            + str(len(values))
        )


def deconstruct(value):
    """Deconstruct the value."""
    try:
        stack_name, param_name = value.split("::")
    except ValueError:
        raise ValueError(
            "output handler requires syntax "
            "of <stack>::<param_name>.  Got: %s" % value
        )

    return stack_name, param_name
