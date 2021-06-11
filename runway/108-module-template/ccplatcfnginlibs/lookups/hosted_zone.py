#!/usr/bin/env python

"""get private hosted zone name"""
from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler
from ccplatcfnginlibs.helpers import route53
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging
import os
import traceback
import sys

TYPE_NAME = "hosted_zone"


class LookupName(LookupHandler):
    """Lookup hosted zone name"""

    @classmethod
    def determine_namespace(cls, context, custom_namespace):
        """function that retrieves the namespace from the config. Looks for custom_namespace, if present"""
        if custom_namespace in context.environment:
            namespace = str(context.environment.get(custom_namespace))
            logging.info(f"Using custom namespace: {namespace}")
        else:
            namespace = str(context.environment.get("namespace"))
            logging.info(f"Using default namespace: {namespace}")
        return namespace

    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=unused-argument
        """
        Handle function to return the name of the private hosted zone attached to the vpc.
        This HZ will be used to create CNAME Resource Records for other resources in the secondary region
        """
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            namespace = cls.determine_namespace(context, "networking_tier_namespace")

            default_department = str(context.environment.get("department")).replace('"', "")
            default_environment = str(context.environment.get("environment")).replace(
                '"', ""
            )

            private_hz_name = (
                f"{default_department}.{namespace}.{default_environment}.aws.swacorp.com."
            )
            return private_hz_name
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

class LookupId(LookupHandler):
    """Lookup hosted zone id"""

    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=unused-argument
        """returns the id of the private hosted zone attached to the vpc"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            lookup_name = LookupName()
            private_hz_name = lookup_name.handle(
                value=value, context=context, provider=provider, kwargs=kwargs
            )
            return route53.get_hz_id(private_hz_name)
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])


class LookupRegion(LookupHandler):
    """Lookup hosted zone region"""

    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=unused-argument
        """returns the CCP:Region tag of the private hosted zone"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            logging.info("Getting region of private hosted zone")
            lookup_id = LookupId()
            private_hz_id = lookup_id.handle(
                value=value, context=context, provider=provider, kwargs=kwargs
            )
            logging.info("Found hosted zone id: %s", private_hz_id)
            return route53.get_hz_region(private_hz_id)
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

class LookupHZExists(LookupHandler):
    """Lookup hosted zone region"""

    @classmethod
    def handle(
        cls, value, context: Context, provider: BaseProvider, **kwargs
    ) -> str:  # pylint: disable=unused-argument
        """returns True/False if a private hosted zone exists within the env"""
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            default_region = str(context.environment.get("region"))

            lookup_id = LookupId()
            private_hz_id = lookup_id.handle(
                value=value, context=context, provider=provider, kwargs=kwargs
            )
            if private_hz_id is None:
                return False
            else:
                lookup_region = LookupRegion()
                private_hz_region = lookup_region.handle(
                    value=value, context=context, provider=provider, kwargs=kwargs
                )
                """ If HZ found in same region, CFN should maintain it """
                if default_region == private_hz_region:
                    return False
                else:
                    logging.info("Private Hosted Zone already exists")
                    return True
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def name(value, context, provider):  # pylint: disable=W0613
    """
    Handle function to return the name of the private hosted zone attached to the vpc.
    This HZ will be used to create CNAME Resource Records for other resources in the secondary region
    """
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        namespace = determine_namespace(context, "networking_tier_namespace")

        default_department = str(context.environment.get("department"))
        default_environment = str(context.environment.get("environment"))

        private_hz_name = (
            f"{default_department}.{namespace}.{default_environment}.aws.swacorp.com."
        )
        return private_hz_name
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def id(value, context, provider):  # pylint: disable=W0613
    """returns the id of the private hosted zone attached to the vpc"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        private_hz_name = name(value, context, provider)
        return route53.get_hz_id(private_hz_name)
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def region(value, context, provider):  # pylint: disable=W0613
    """returns the CCP:Region tag of the private hosted zone"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        private_hz_id = id(value, context, provider)
        return route53.get_hz_region(private_hz_id)
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def exists(value, context, provider):  # pylint: disable=W0613
    """returns True/False if a private hosted zone exists within the env"""
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        default_region = str(context.environment.get("region"))

        private_hz_id = id(value, context, provider)
        if private_hz_id is None:
            return False
        else:
            private_hz_region = region(value, context, provider)
            """ If HZ found in same region, CFN should maintain it """
            if default_region == private_hz_region:
                return False
            else:
                logging.info("Private Hosted Zone already exists")
                return True
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def determine_namespace(context, custom_namespace):
    """function that retrieves the namespace from the config. Looks for custom_namespace, if present"""
    try:
        if custom_namespace in context.environment:
            namespace = str(context.environment.get(custom_namespace))
            logging.info(f"Using custom namespace: {namespace}")
        else:
            namespace = str(context.environment.get("namespace"))
            logging.info(f"Using default namespace: {namespace}")
        return namespace
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])