# pylint: disable=broad-except
""" iam helper functions """
import boto3
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

SERVICE_ROLE_NAMES = {
    "autoscaling": "AWSServiceRoleForAutoScaling",
    "dynamodb.application-autoscaling": "AWSServiceRoleForApplicationAutoScaling_DynamoDBTable",
    "ops.apigateway": "AWSServiceRoleForAPIGateway",
}


def get_iam_client(region):  # pragma: no cover
    """ Returns the IAM client """
    return boto3.client("iam", region_name=region)


def get_service_role_arn(role_name, region):
    """
    Returns the service role arn for the
    role_name if exists or None if not
    """
    response = None
    try:
        response = get_iam_client(region).get_role(RoleName=role_name)["Role"]["Arn"]
    except Exception as exception:
        LOGGER.error("Unable to find service role for %s: %s", role_name, exception)
    return response


def create_service_role(service_prefix, region):
    """
    Determines if service role exists using role_name. 
    If it does, returns arn.
    If not, creates the service role using the associated service prefix.
    Returns None if unsuccessful.
    """
    resp = get_service_role_arn(SERVICE_ROLE_NAMES[service_prefix], region)
    if not resp:
        try:
            resp = get_iam_client(region).create_service_linked_role(
                AWSServiceName=f"{service_prefix}.amazonaws.com"
            )["Role"]["Arn"]
            LOGGER.info("Service linked role created: %s", resp)
        except Exception as exception:
            LOGGER.error(
                "Error creating service role %s: %s",
                SERVICE_ROLE_NAMES[service_prefix],
                exception,
            )
    return resp


def create_autoscaling_service_role(region):
    """ Creates the autoscaling service role. Returns None if unsuccessful """
    return create_service_role("autoscaling", region)


def create_ddb_app_autoscaling_service_role(region):
    """
    Creates the dynamodb application autoscaling service role.
    Returns None if unsuccessful
    """
    return create_service_role("dynamodb.application-autoscaling", region)

def create_api_gateway_service_role(region):
    """
    Creates the api gateway service role.
    Returns None if unsuccessful
    """
    return create_service_role("ops.apigateway", region)
