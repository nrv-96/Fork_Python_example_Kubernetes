"""cloudformation helper functions"""
import boto3
import os
from botocore.exceptions import ClientError
from botocore.config import Config
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER


def get_cfn_client(region=os.getenv("AWS_DEFAULT_REGION")):  # pragma: no cover
    """
  boto3 client for cloudformation
  This is here for unit testing
  :return:
  """
    config = Config(retries=dict(max_attempts=20))
    session = boto3.session.Session()
    return session.client("cloudformation", config=config, region_name=region)


def get_output(stack, desired_output):
    """get output from stack"""
    cfn = get_cfn_client()

    stack_details = cfn.describe_stacks(StackName=stack)
    value = ""

    if "Outputs" in stack_details["Stacks"][0]:
        cluster_stack_outputs = stack_details["Stacks"][0]["Outputs"]
        for output in cluster_stack_outputs:
            if output["OutputKey"].upper() == desired_output.upper():
                value = output["OutputValue"]

    if value == "":
        raise Exception(desired_output + " not found in stack " + stack)
    else:
        return value


def get_all_outputs(stack):
    """get all outputs from stack"""
    cfn = get_cfn_client()
    outputs = []
    try:
        stack_outputs = cfn.describe_stacks(StackName=stack)["Stacks"][0]
        if "Outputs" in stack_outputs:
            outputs = stack_outputs["Outputs"]
    except ClientError as e:
        LOGGER.error(f"Unable to get stack outputs for stack: {stack}")
        raise e

    return outputs


def get_kms_key_id(account_id, region):
    """get kms key id"""
    exports = get_cfn_client(region).list_exports()["Exports"]
    matches = []
    for export in exports:
        if export["Name"] == f"{account_id}-{region}-swa-kms-key-arn":
            matches.append(export)
    if len(matches) != 1:
        LOGGER.error("Could not find SWA KMS Key ID")
        raise Exception("Could not find SWA KMS Key ID")
    else:
        LOGGER.debug(f"SWA KMS Key ID: {matches[0]['Value']}")
        return matches[0]["Value"]


def stack_exists(name):
    """check stack exists"""
    cfn = get_cfn_client()
    try:
        data = cfn.describe_stacks(StackName=name)
    except ClientError as e:
        return False
    return True
