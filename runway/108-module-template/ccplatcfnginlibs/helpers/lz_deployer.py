"""
Helper used to deploy artifacts using the landing zone distributed deployment engine

This helper expects the following ssm parameters to exist in the account
that the helper is executed.

landing_zone_bucket_name - The name of the S3 bucket use to upload the artifact for deployment
landing_zone_api_id - The api_id of the api gateway used to make landing zone api calls
landing_zone_kms_key - The kms key used to encrypt the artifact uploaded to the bucket
"""

import sys
import traceback
import uuid
import base64
import time
import json
import concurrent.futures
from datetime import datetime, timedelta
import requests
import boto3
import ssm
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

API_CALL_SLEEP = 10
DEFAULT_TIMEOUT = 900


def get_s3_client(region):  # pragma: no cover
    """ Returns the S3 client """
    return boto3.client("s3", region_name=region)


def get_lz_bucket():
    """ Retrieves the landing zone bucket name from parameter store """
    return ssm.get_parameter("landing_zone_bucket_name")


def get_lz_api_id():
    """ Retrieves the landing zone api id from parameter store """
    return ssm.get_parameter("landing_zone_api_id")


def get_lz_kms_key():
    """ Retrieves the landing zone kms key id from parameter store """
    return ssm.get_parameter("landing_zone_kms_key")


def deploy_artifacts(artifact_paths, s3_prefix, region, env, timeout=DEFAULT_TIMEOUT):
    """
    Deploys multiple deployment artifacts simultaneously.
    Returns:
      True - if all deployments successful
      False - if any deployment not successful
    """
    response = True
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(
                deploy_artifact, artifact_path, s3_prefix, region, env, timeout
            ): artifact_path
            for artifact_path in artifact_paths
        }

        for future in concurrent.futures.as_completed(futures, timeout=timeout + 60):
            artifact_path = futures[future]
            response = response and future.result()
    return response


def deploy_artifact(artifact_path, s3_prefix, region, env, timeout=DEFAULT_TIMEOUT):
    """
    Deploys a deployment artifact.
    Returns:
      True - if deployment successful
      False - if deployment not successful
    """
    successful = False
    try:
        etag = upload_artifact(artifact_path, s3_prefix, region)
        if etag:
            successful = check_deployment(etag, region, env, timeout)
    except Exception as exc:
        LOGGER.error(
            "Exception occurred while deploying artifact %s: %s", artifact_path, exc
        )
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(
            exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout
        )
    return successful


def upload_artifact(artifact_path, s3_prefix, region):
    """
    Uploads the artifact for deployment.
    Returns:
      Etag - etag id from s3 response
    """
    response = None
    key = f"{s3_prefix}/{artifact_path.split('/')[-1]}"
    api_resp = put_object(get_lz_bucket(), key, artifact_path, region)
    LOGGER.debug("Response: %s", api_resp)
    if "ETag" in api_resp:
        response = api_resp["ETag"].replace('"', "")

    return response


def put_object(bucket, key, object_path, region):
    """
    Puts the object defined by the object path in the
    S3 bucket using the given key.
    """
    LOGGER.debug("bucket: %s", bucket)
    LOGGER.debug("key: %s", key)
    LOGGER.debug("object_path: %s", object_path)
    LOGGER.debug("region: %s", region)
    LOGGER.debug("get_lz_kms_key: %s", get_lz_kms_key())
    with open(object_path, "rb") as file:
        return get_s3_client(region).put_object(
            Bucket=bucket,
            Key=key,
            Body=file.read(),
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=get_lz_kms_key(),
            ACL="bucket-owner-full-control",
        )


def check_deployment(etag, region, env, timeout):
    """
    Checks if the deployment was successful.
    Returns:
      True - if deployment completed successfully
      False - if deployment not successful
    """
    endpoint_url = f"https://{get_lz_api_id()}.execute-api.{region}.amazonaws.com/{env}/deployment/{etag}"
    credential = base64.b64encode(str(uuid.uuid1()).encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credential}",
    }
    status = None
    end_time = datetime.now() + timedelta(seconds=timeout)
    LOGGER.debug("end_time: %s", end_time)
    while status is None and datetime.now() < end_time:
        time.sleep(API_CALL_SLEEP)
        LOGGER.debug("calling api")
        api_resp = requests.get(endpoint_url, headers=headers)
        LOGGER.debug("api response: %s", api_resp)
        api_resp.raise_for_status()
        resp_json = json.loads(api_resp.text)
        if "Items" in resp_json:
            status = deployment_status(resp_json["Items"])
    return bool(status)


def deployment_status(items):
    """
    Iterates though all deployment items and determines status
    Returns:
      True - if deployment in CREATE_COMPLETE or UPDATE_COMPLETE status
      False - if deployment in and FAILED or ROLLBACK status
      None - if deployment not in any COMPLETE, FAILED or ROLLBACK state
    """
    response = None
    success_matches = ["CREATE_COMPLETE", "UPDATE_COMPLETE"]
    failed_matches = ["FAILED", "ROLLBACK"]
    for item in items:
        if any(x in item["Message"]["S"] for x in success_matches):
            response = True
        elif any(x in item["Message"]["S"] for x in failed_matches):
            response = False
    return response
