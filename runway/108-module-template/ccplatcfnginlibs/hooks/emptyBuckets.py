"""hook to empty buckets"""
import boto3
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER
import os
import yaml

def get_s3_resource():  # pragma: no cover
    """
    boto3 resource for s3
    This is here for unit testing
    :return:
    """
    return boto3.resource("s3")


def hook(provider, context, **kwargs):  # pragma: no cover
    """hook to empty buckets"""

    department = context.environment["department"]
    region = context.environment["region"]
    namespace = context.environment["namespace"]
    module_config = context.environment["module_config"]

    with open(module_config) as file:
        bucket_info= yaml.load(file, Loader=yaml.FullLoader)["vBucketList"]
        buckets = list_buckets(bucket_info, department, region, namespace)
        remove_bucket_logging(buckets)
        empty(buckets)

    return True


def list_buckets(bucket_info, department, region, namespace):
    """list buckets based on bucket information"""
    buckets = []
    for bucket in bucket_info:
        buckets.append(f"{department}-{region}-{namespace}-{bucket['name']}")
        if "crossRegion" in bucket:
            buckets.append(f"{department}-{bucket['crossRegion']}-{namespace}-{bucket['name']}")
    return buckets


def remove_bucket_logging(bucket_list):
    """ Removes logging from s3 buckets """
    LOGGER.info(f'Removing logging from buckets {bucket_list}')
    s3_resource = get_s3_resource()
    for bucket in bucket_list:
        retries = 3
        while retries > 0:
            try:
                LOGGER.info(f"Removing logging from {bucket}")
                s3_bucket_logging = s3_resource.BucketLogging(bucket)
                s3_bucket_logging.put(BucketLoggingStatus={})
                break
            except Exception as e: #pragma: no cover
                if "NoSuchBucket" in str(e):
                    break
                print(e)
                retries -= 1
        if retries == 0:
            raise Exception("Error removing logging from S3 Buckets")
    return "Logging Disabled"


def empty(bucket_list):
    """empty buckets"""

    s3_resource = get_s3_resource()

    for bucket in bucket_list:
        retries = 3
        while retries > 0:
            try:
                LOGGER.info(f"Emptying {bucket}")
                s3_bucket = s3_resource.Bucket(bucket)
                s3_bucket.objects.all().delete()
                s3_bucket.object_versions.delete()
                s3_bucket.delete()
                break
            except Exception as e:
                if "NoSuchBucket" in str(e):
                    break
                print(e)
                retries -= 1
        if retries == 0:
            raise Exception("Error tearing down S3 Buckets")

    return True
