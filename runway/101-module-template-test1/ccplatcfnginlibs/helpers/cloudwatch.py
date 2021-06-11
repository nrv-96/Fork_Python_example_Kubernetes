"""cloudwatch helper functions"""
import boto3

def get_logs_client(): # pragma: no cover
  """
  boto3 client for logs
  This is here for unit testing
  :return:
  """
  return boto3.client("logs")

def set_log_retention(log_group, env):
  """sets log retention"""
  logs_client = get_logs_client()
  logs_client.put_retention_policy(
                                    logGroupName=log_group,
                                    retentionInDays=get_log_retention_setting(env)
                                  )
  return get_log_retention_setting(env)

def get_log_retention_setting(env):
  """gets log retention"""
  log_retention = {
                  'lab'  : 1,
                  'dev'  : 5,
                  'qa'   : 30,
                  'prod' : 90
                }

  return log_retention[env]
