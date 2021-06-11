# pylint: disable=broad-except
""" kms helper functions """
import boto3
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER


def get_kms_client(region):
    """ Returns the kms client """
    return boto3.client("kms", region_name=region)


def grant_exists_for_role(kms_key_id, role_arn, region):
    """ Determine if the grant for the autoscaler service role exists """
    resp = get_kms_client(region).list_grants(KeyId=kms_key_id)
    trunc = resp["Truncated"]
    found = role_exists_in_grants(role_arn, resp["Grants"])
    while not found and trunc:
        resp = get_kms_client(region).list_grants(
            KeyId=kms_key_id, Marker=resp["NextMarker"]
        )
        trunc = resp["Truncated"]
        found = role_exists_in_grants(role_arn, resp["Grants"])
    return found


def role_exists_in_grants(role_arn, grant_list):
    """ Determines is the passed role exists in the list of grants """
    result = False
    for grant in grant_list:
        if role_arn == grant["GranteePrincipal"]:
            result = True
            break
    return result


def create_grant(kms_key_id, role_arn, region):
    """ Creates a grant for the passed KMS key and role. Returns False if unsuccessful """
    resp = True
    ops = [
        "Encrypt",
        "Decrypt",
        "ReEncryptFrom",
        "ReEncryptTo",
        "GenerateDataKey",
        "GenerateDataKeyWithoutPlaintext",
        "DescribeKey",
        "CreateGrant",
    ]
    try:
        result = get_kms_client(region).create_grant(
            KeyId=kms_key_id, GranteePrincipal=role_arn, Operations=ops
        )
        LOGGER.info(
            "Grant created for key %s and role %s: %s", kms_key_id, role_arn, result
        )
    except Exception as exception:
        LOGGER.error(
            "Unable to create grant for key %s and role %s: %s",
            kms_key_id,
            role_arn,
            exception,
        )
        resp = False
    return resp
