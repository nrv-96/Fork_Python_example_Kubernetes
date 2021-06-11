"""kubectl helper functions"""
import subprocess
from os import path, walk, mkdir, chmod
from kubernetes import client, config
from os import stat as os_stat
import stat
import time

def setup_kube_ctl(clustername):  # pragma: no cover
  """setup kube control"""
  subprocess.call("bash -c 'k8s/scripts/setup_kube_ctl.sh %s'" % (clustername), shell=True)

def delete_all_client_namespaces():  # pragma: no cover
  """delete all client namespaces"""
  config.load_kube_config()

  v1 = client.CoreV1Api()

  namespaces = v1.list_namespace(watch=False).items
  for namespace in namespaces:
    namespace_name = namespace.metadata.name
    deleted_namespaces = []
    if namespace_name not in ['kube-system', 'default', 'kube-node-lease', 'kube-public']:
      print("Deleting Kubernetes Namespace: " + namespace_name)
      v1.delete_namespace(name=namespace_name)
      deleted_namespaces.append(namespace_name)

  wait = True
  sleep_time = 5
  sleep_incrementor = 2
  while wait:
    wait = False
    living_namespaces = v1.list_namespace(watch=False).items
    for namespace in living_namespaces:
      if namespace.metadata.name in deleted_namespaces:
        wait = True
        if sleep_time > 300:
          raise Exception("TIMEOUT WAITING FOR NAMESPACES TO DELETE")
        else:
          print("Namespace: " + namespace.metadata.name + " is still alive. Waiting " + str(sleep_time))
        time.sleep(sleep_time)
        sleep_time = sleep_time * sleep_incrementor

def fix_permissions(targetdir): # pragma: no cover
  """fix permissions"""

  for root, dirs, files in walk(targetdir, topdown=False):
    for name in files:
      filename = path.join(targetdir+"/",name)
      if name.endswith(".sh"):
        st = os_stat(filename)
        chmod(filename, st.st_mode | stat.S_IEXEC)

def wait_for_namespace_delete(namespace_wait): # pragma: no cover
  """ wait for a given namespace to delete """
  config.load_kube_config()
  v1 = client.CoreV1Api()
  wait = True
  sleep_time = 5
  sleep_incrementor = 2
  while wait:
    wait = False
    living_namespaces = v1.list_namespace(watch=False).items
    for namespace in living_namespaces:
      if namespace.metadata.name == namespace_wait:
        wait = True
        if sleep_time > 300:
          raise Exception("TIMEOUT WAITING FOR NAMESPACES TO DELETE")
        else:
          print("Namespace: " + namespace.metadata.name + " is still alive. Waiting " + str(sleep_time))
        time.sleep(sleep_time)
        sleep_time = sleep_time * sleep_incrementor

def retrieve_service_config(service_name, namespace):
  """ retrieves the configuration of a service """
  config.load_kube_config()
  v1 = client.CoreV1Api()
  response = None
  try:
    response = v1.read_namespaced_service(name=service_name, namespace=namespace).to_dict()
  except Exception as exception:
    if exception.reason == 'Not Found':
      print(f"Unable to find service {service_name} in namespace {namespace}")
    else:
      print(f"Error occurred while attempting to retrieve service {service_name} in namespace {namespace}: {exception}")
  return response