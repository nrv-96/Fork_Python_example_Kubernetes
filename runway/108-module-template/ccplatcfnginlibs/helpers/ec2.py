"""ec2 helper functions"""
import boto3

def get_ec2_client(): # pragma: no cover
  """
  boto3 client for ec2
  This is here for unit testing
  :return:
  """
  return boto3.client("ec2")

def delete_eni_orphans(vpc_id):
  """delete orphans"""
  ec2 = get_ec2_client()
  print(f"Going thru ENI in VPC: {vpc_id} to delete orphans")
  eni_orphans = list(filter(lambda eni: (vpc_id == eni['VpcId'] and 'available' == eni['Status']), 
                                            ec2.describe_network_interfaces()['NetworkInterfaces'])) 
  deleted_orphans = []
  for eni in eni_orphans:
    ec2.delete_network_interface(NetworkInterfaceId=eni['NetworkInterfaceId'])
    deleted_orphans.append(eni)
    print(f"Deleted ENI orphan: {eni['NetworkInterfaceId']}")

  return deleted_orphans