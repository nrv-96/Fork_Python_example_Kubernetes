"""sts helper functions"""
import boto3

def get_sts_client():  # pragma: no cover
    """
    boto3 client for sts
    This is here for unit testing
    :return:
    """
    return boto3.client("sts")

def get_account_id():
    """get account id"""
    return get_sts_client().get_caller_identity()["Account"]