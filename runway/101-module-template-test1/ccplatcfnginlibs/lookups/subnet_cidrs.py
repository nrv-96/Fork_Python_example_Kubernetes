#!/usr/bin/env python
""" return CIDRs for subnet ids """

from runway.cfngin.context import Context
from runway.cfngin.providers.base import BaseProvider
from runway.lookups.handlers.base import LookupHandler
from boto3 import client
import boto3
import traceback
import sys
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as logging

TYPE_NAME = 'subnet_cidrs'

class Lookup(LookupHandler):
    """ lookup cidrs by subnet ids """

    @classmethod
    def get_ec2_client(cls): # pragma: no cover
        """ returns the ec2 client """
        return client("ec2")

    @classmethod
    def handle(cls, value, context: Context, provider: BaseProvider, **kwargs) -> str:  # pylint: disable=unused-argument
        """ handles the lookup """
        try:
            logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
            cidrs = []
            subnet_ids = str(value).split(',')
            subnets = cls.get_ec2_client().describe_subnets(SubnetIds=subnet_ids)['Subnets']

            for subnet in subnets:
                cidrs.append(subnet['CidrBlock'])

            return ",".join(cidrs)
        except BaseException as error:
            logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
            logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
            raise error.with_traceback(sys.exc_info()[2])

## Remove old lookup
def get_ec2_client():
    ''' returns the ec2 client'''
    return boto3.client("ec2")

## Remove old lookup
def handle(value, context, provider):  # pylint: disable=W0613
    ''' handles the lookup '''
    try:
        logging.info(f'Running lookup for module: {str(context.environment["module_name"])}')
        cidrs = []
        subnet_ids = str(value).split(',')
        subnets = get_ec2_client().describe_subnets(SubnetIds=subnet_ids)['Subnets']

        for subnet in subnets:
            cidrs.append(subnet['CidrBlock'])

        return ",".join(cidrs)
    except BaseException as error:
        logging.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        logging.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])