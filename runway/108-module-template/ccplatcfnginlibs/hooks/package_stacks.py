"""Loop through stacks and package tamplates"""

# We are disabling the protected-access (W0212) warning for pylint because
# we are making calls on protected methods in the awscli libraries.
# pylint: disable=protected-access
# Disable unused arguments for the call to hook. Stacker uses named arguments so we cannot
# use the underscore to satisfy pylint for unused arguments.
# pylint: disable=unused-argument
import os
import subprocess
import traceback
import sys
import shutil
from distutils.dir_util import copy_tree

from collections import namedtuple
from boto3 import session
from awscli.customizations.cloudformation.package import PackageCommand
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

ARGS = {
    "region": "us-west-2",
    "verify_ssl": True,
    "kms_key_id": None,
    "force_upload": True,
    "metadata": None,
    "use_json": True,
}


def hook(provider, context, **kwargs):
    """ Hook called by stacker """
    try:
        LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
        packager = get_package_command()
        ARGS["region"] = context.environment.get("region")
        ARGS["s3_bucket"] = context.environment.get("stacker_bucket_name")
        for stack in context.config.stacks:
            if not context.stack_names or stack.name in context.stack_names:
                if stack.template_path.endswith(".output"):
                    LOGGER.info("Packaging stack %s", stack.name)
                    ARGS["s3_prefix"] = stack.name
                    template_file = determine_template_file(stack.template_path)
                    ARGS["template_file"] = template_file
                    template_file_out = stack.template_path.replace(
                        ".output", ".{}.output".format(context.environment.get("region"))
                    )
                    ARGS["output_template_file"] = template_file_out
                    stack.template_path = template_file_out
                    args_object = namedtuple("Args", ARGS.keys())(**ARGS)
                    packager._run_main(args_object, args_object)
        return True
    except BaseException as error:
        LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
        LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
        raise error.with_traceback(sys.exc_info()[2])

def get_package_command():
    """ Return the PackageCommand from AWS CLI """
    cfn_session = session.Session()
    return PackageCommand(cfn_session._session)


def file_exists(file_path):
    """ Determines if the requested files exists """
    return os.path.isfile(file_path)


def determine_template_file(output_path):
    """ Determines if the template file uses a yml or yaml extension """
    test_file = output_path.replace(".output", ".yml")
    if file_exists(test_file):
        return test_file
    test_file = output_path.replace(".output", ".yaml")
    if file_exists(test_file):
        return test_file
    raise Exception("Template file ending in yml or yaml cannot be found")

