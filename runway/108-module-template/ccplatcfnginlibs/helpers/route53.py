"""route53 helper functions"""
import boto3
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER


def get_r53_client():  # pragma: no cover
    """
    boto3 client for route53
    This is here for unit testing
    :return:
    """
    return boto3.client("route53")


def delete_k8s_external_dns_orphans(hosted_zone, region):
    """delete orphans"""
    route53 = get_r53_client()
    changes = []
    print("Going through the hosted zone: " + hosted_zone + " to delete orphans")
    records_to_delete = get_k8s_external_dns_orphans(route53, hosted_zone, region)
    for record in records_to_delete:
        changes.append({"Action": "DELETE", "ResourceRecordSet": record})
    if len(changes) != 0:
        print("Applying the changes: \n" + str(changes))
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone, ChangeBatch={"Changes": changes}
        )
    return changes


def get_k8s_external_dns_orphans(route53, hosted_zone, region):
    """get orphans"""
    response = route53.list_resource_record_sets(HostedZoneId=hosted_zone)
    record_sets = response["ResourceRecordSets"]
    while response["IsTruncated"]:
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone,
            StartRecordName=response["NextRecordName"],
            StartRecordType=response["NextRecordType"],
        )
        record_sets.extend(response["ResourceRecordSets"])
    records_to_delete = []
    external_dns_record_names = set()
    for i in record_sets:
        if i["Type"] == "TXT":
            for x in i["ResourceRecords"]:
                if "Value" in x and "external-dns" in x["Value"]:
                    external_dns_record_names.add(i["Name"])
    print(f"external_dns_record_names: {external_dns_record_names}")
    for j in record_sets:
        if j["Name"] in external_dns_record_names and region in j["SetIdentifier"]:
            records_to_delete.append(j)
    return records_to_delete


def delete_all_orphans(hosted_zone):
    """delete orphans"""
    route53 = get_r53_client()
    changes = []
    print("Going through the hosted zone: " + hosted_zone + " to delete orphans")

    records_to_delete = get_all_orphans(route53, hosted_zone)
    for record in records_to_delete:
        changes.append({"Action": "DELETE", "ResourceRecordSet": record})

    if len(changes) != 0:
        print("Applying the changes: \n" + str(changes))
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone, ChangeBatch={"Changes": changes}
        )
    return changes


def get_all_orphans(route53, hosted_zone):
    """get orphans"""
    response = route53.list_resource_record_sets(HostedZoneId=hosted_zone)
    record_sets = response["ResourceRecordSets"]
    while response["IsTruncated"]:
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone,
            StartRecordName=response["NextRecordName"],
            StartRecordType=response["NextRecordType"],
        )
        record_sets.extend(response["ResourceRecordSets"])
    records_to_delete = []
    for i in record_sets:
        if i["Type"] != "NS" and i["Type"] != "SOA":
            print(i)
            records_to_delete.append(i)
    return records_to_delete


def get_hz_id(hz_name):
    """get id of hosted zone"""
    route53 = get_r53_client()
    response = route53.list_hosted_zones_by_name(DNSName=hz_name)

    LOGGER.info("Getting hosted zone ID")
    LOGGER.debug("Response: %s", response)
    if response["HostedZones"]:
        LOGGER.debug("Found Hosted Zones: %s", response["HostedZones"])
        for hzone in response["HostedZones"]:
            LOGGER.debug("Parsing Response Segment: %s", hzone)
            if hzone["Name"] == hz_name:
                hzone_id = hzone["Id"].split("/")[2]
                LOGGER.info("Got hosted zone id: %s", hzone_id)
                return hzone_id

    LOGGER.error("Failed to get hosted zone ID")
    return None


def get_hz_region(hz_id):
    """get hosted zone's region based on CCP:Region tag"""
    route53 = get_r53_client()
    LOGGER.info("Getting hosted zone region")
    response = route53.list_tags_for_resource(
        ResourceType="hostedzone", ResourceId=hz_id
    )
    region_tag = next(
        item
        for item in response["ResourceTagSet"]["Tags"]
        if item["Key"] == "CCP:Region"
    )
    region_value = region_tag["Value"]
    LOGGER.info("Found region: %s", region_value)
    return region_value
