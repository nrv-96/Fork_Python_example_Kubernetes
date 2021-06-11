#!/usr/bin/env python
from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler

import traceback
import sys

"""get all available subnets"""
from ccplatcfnginlibs.helpers import ssm  # pragma: no cover
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

TYPE_NAME = "availableSubnets"


class Lookup(LookupHandler):
    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=W0613
        """availableSubnets"""
        try:
            subnet_types = str(value).split(",")

            namespace = cls.determine_namespace(context, "networking_tier_namespace")

            stack_outputs = ssm.get_stack_outputs("vpc", "vpc", namespace)
            output_keys = dict(stack_outputs).keys()
            key_extension = "subnet"
            available_subnets = []

            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')

            # iterate through keys in output
            for key in output_keys:
                for subnet_type in subnet_types:
                    subnet_prefix = str(subnet_type).strip().lower() + key_extension

                    if str(key).lower().startswith(subnet_prefix) and str(
                        stack_outputs[key]
                    ).startswith(key_extension):
                        available_subnets.append(stack_outputs[key])

            # print number of available subnets
            print(
                "Found {0} available subnets for types {2} : {1} ".format(
                    len(available_subnets), available_subnets, str(subnet_types)
                )
            )

            return ",".join(available_subnets)
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


## Remove old lookup


def handle(value, context, provider):  # pylint: disable=W0613
    """availableSubnets"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        subnet_types = str(value).split(",")

        namespace = determine_namespace(context, "networking_tier_namespace")

        stack_outputs = ssm.get_stack_outputs("vpc", "vpc", namespace)
        output_keys = dict(stack_outputs).keys()
        key_extension = "subnet"
        available_subnets = []

        # iterate through keys in output
        for key in output_keys:
            for subnet_type in subnet_types:
                subnet_prefix = str(subnet_type).strip().lower() + key_extension

                if str(key).lower().startswith(subnet_prefix) and str(
                    stack_outputs[key]
                ).startswith(key_extension):
                    available_subnets.append(stack_outputs[key])

        # print number of available subnets
        print(
            "Found {0} available subnets for types {2} : {1} ".format(
                len(available_subnets), available_subnets, str(subnet_types)
            )
        )

        return ",".join(available_subnets)
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
