"""eks helper functions"""
import boto3
import time

def get_eks_client(): # pragma: no cover
  """
  boto3 client for eks
  This is here for unit testing
  :return:
  """
  return boto3.client("eks")

def describe_cluster(eks_cluster_name):
    """
    This method is utilized to provide missing functionality from cloudformation. Below is a list of what it does.
    describe eks cluster
    """
    eks_client = get_eks_client()
    return eks_client.describe_cluster( name=eks_cluster_name )

def configure_cluster(eks_cluster_name, environment_name):
    """
    This method is utilized to provide missing functionality from cloudformation. Below is a list of what it does.
        Enable Logging
        Enable Cluster Private endpoint configuration based on environment level
        Dev QA and PROD are set to Private only access
        Lab accounts are set to Private and Public access enabled
    :return:
    """
    update_occurred = False
    eks_client = get_eks_client()
    eks_cluster = describe_cluster( eks_cluster_name )
    if not eks_cluster['cluster']['logging']['clusterLogging'][0]['enabled']:
        logging_types = ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']
        response = eks_client.update_cluster_config(
                                            name=eks_cluster_name,
                                            logging={
                                                'clusterLogging': [ {
                                                    'types': logging_types,
                                                    'enabled': True
                                            }, ]
                                            }
                                        )
        wait_for_cluster_update(eks_cluster_name , response['update']['id'])
        update_occurred = True
    if ((environment_name == 'lab')
        and
    (not eks_cluster['cluster']['resourcesVpcConfig']['endpointPrivateAccess'] or
        not eks_cluster['cluster']['resourcesVpcConfig']['endpointPublicAccess'])):
        response = eks_client.update_cluster_config(
                                        name=eks_cluster_name,
                                        resourcesVpcConfig = {
                                            'endpointPrivateAccess': True,
                                            'endpointPublicAccess': True
                                        })
        wait_for_cluster_update(eks_cluster_name , response['update']['id'])
        update_occurred = True
    if ((environment_name == 'dev' or environment_name == 'qa' or environment_name == 'prod')
        and
    (not eks_cluster['cluster']['resourcesVpcConfig']['endpointPrivateAccess'] or
        eks_cluster['cluster']['resourcesVpcConfig']['endpointPublicAccess']
    )):
        response = eks_client.update_cluster_config(
                                        name=eks_cluster_name,
                                        resourcesVpcConfig = {
                                            'endpointPrivateAccess': True,
                                            'endpointPublicAccess': False
                                        })
        wait_for_cluster_update(eks_cluster_name , response['update']['id'])
        update_occurred = True

    return update_occurred

def wait_for_cluster_update(eks_cluster_name, update_id):
  """
  This method is utilized to provide missing functionality from cloudformation. Below is a list of what it does.
    Waits for the EkS cluster to be in an active state before processing any more updates
  :return:
  """

  eks_client = get_eks_client()
  sleep_time = 5
  sleep_incrementor = 2

  while eks_client.describe_update(
                                    name=eks_cluster_name,
                                    updateId=update_id
                                  )['update']['status'] == "InProgress":
    if sleep_time > 1800:
      raise Exception("TIMEOUT WAITING FOR EKS CLUSTER TO UPDATE")
    else:
      print("Cluster: " + eks_cluster_name + " is still updating. Waiting " + str(sleep_time))
      time.sleep(sleep_time)
      sleep_time = sleep_time * sleep_incrementor


def namespace_from_cluster_name(cluster_name):
    parts = cluster_name.split('-')
    return '-'.join(parts[0-len(parts):-4])


def region_from_cluster_name(cluster_name):
    parts = cluster_name.split('-')
    return '-'.join(parts[-3:])


def environment_from_cluster_name(cluster_name):
    return cluster_name.split('-')[-4]

