#!/usr/bin/env python
"""Sample Hook"""

from os import environ
# Sample Hook serves as reference and should be removed when creating new module
def hook(provider, context, **kwargs):
    """validate context region with aws default region"""
    # check if AWS_DEFAULT_REGION is set
    if 'AWS_DEFAULT_REGION' not in environ:
        return True
    # check if region in context environment
    elif 'region' not in context.environment:
        return True
    else:
        return context.environment['region'] == environ.get('AWS_DEFAULT_REGION')
