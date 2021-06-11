"""ssm helper functions.
These are here because CFN doesn't allow for encrypted parameters"""
import boto3
import cloudformation
import os
from botocore.config import Config
from botocore.exceptions import ClientError


def get_ssm_client(region=os.getenv("AWS_DEFAULT_REGION")): # pragma: no cover
  """
  boto3 client for ssm
  This is here for unit testing
  :return:
  """
  config = Config(
      retries = dict(
          max_attempts = 20
      )
  )
  session = boto3.session.Session()
  return session.client('ssm', config=config, region_name=region)


def get_kms_key(): # pragma: no cover
  """
  get KMS Key to use for SSM secure string
  This is here for unit testing
  :return:
  """
  return cloudformation.get_output("EC-KmsKey", "KmsKeyID")


def put_secure_string_parameter(name, value, description, tagDict):
  """
  write a secure string parameter
  :param name: (string) SSM Parameter Name
  :param value: (string) SSM Parameter Value
  :param description: (string) SSM Parameter Description
  :param tagDict: (dict) Dictionary of Tags
  :return:
  """

  ssm = get_ssm_client()

  # KMS Key to use for SSM secure string
  key_id = get_kms_key()

  # Write the SSM parameter
  ssm.put_parameter(
      Name=name,
      Description=description,
      Value=value,
      Type='SecureString',
      Overwrite=True,
      KeyId = key_id
  )

  # Tag SSM parameter
  ssm.add_tags_to_resource(
      ResourceType='Parameter',
      ResourceId=name,
      Tags=[dict(Key = k, Value = v) for k, v in tagDict.items()]
  )

  return True


def put_string_parameter(name, value, description, tagDict, region=os.getenv("AWS_DEFAULT_REGION")):
  """
  write a secure string parameter
  :param name: (string) SSM Parameter Name
  :param value: (string) SSM Parameter Value
  :param description: (string) SSM Parameter Description
  :param tagDict: (dict) Dictionary of Tags
  :return:
  """

  ssm = get_ssm_client(region)

  # Write the SSM parameter
  ssm.put_parameter(
      Name=name,
      Description=description,
      Value=value,
      Type='String',
      Overwrite=True
  )

  # Tag SSM parameter
  ssm.add_tags_to_resource(
      ResourceType='Parameter',
      ResourceId=name,
      Tags=[dict(Key = k, Value = v) for k, v in tagDict.items()]
  )

  return True


def get_module_parameters(path, region=os.getenv("AWS_DEFAULT_REGION")):
  ssm = get_ssm_client(region)

  params = ssm.get_parameters_by_path(Path = path, Recursive = True)
  return_params = params['Parameters']
  while "NextToken" in params:
    params =  ssm.get_parameters_by_path(Path = path, Recursive = True, NextToken = params['NextToken'])
    return_params.extend(params['Parameters'])

  return return_params


def delete_parameters(parameters):
  ssm = get_ssm_client()
  n = 10
  groups_of_10 = [parameters[i * n:(i + 1) * n] for i in range((len(parameters) + n - 1) // n )]
  for group in groups_of_10:
    ssm.delete_parameters(Names = group)
  return True


def get_parameter(parameter):
  ''' retrieve parameter '''
  ssm = get_ssm_client()
  param_value = None
  try:
    param_value = ssm.get_parameter(Name=parameter, WithDecryption=True)['Parameter']['Value']
  except ClientError as error:
    if error.response['Error']['Code'] == 'ParameterNotFound':
      raise Exception(f'Parameter \'{parameter}\' is not found in SSM')
    else:
      raise Exception(f'Error occurred while retreiving parameter \'{parameter}\' from SSM: {str(error)}')

  return param_value


def get_stack_parameter(stack_resource_name, stack_name, parameter, namespace):
  ''' Get SSM parameter based on provided stack resource, stack name, param name and namespace'''
  module_name = f"cloud-common-{stack_resource_name}-module"
  path = f"/ccplat/{namespace}/{module_name}/{stack_name}/{parameter}"

  return get_parameter(path)


def get_stack_outputs(stack_resource_name, stack_name, namespace):
  ''' Get SSM parameters based on provided stack resource, stack name and namespace'''
  module_name = f"cloud-common-{stack_resource_name}-module"
  path = f"/ccplat/{namespace}/{module_name}/{stack_name}"

  module_params =  get_module_parameters(path)
  stack_outputs = {}

  for param in module_params:
        key = param["Name"].split("/")[-1]
        value = param["Value"]
        stack_outputs[key] = value;

  return stack_outputs


def delete_parameter(name):
  """delete parameter"""
  ssm = get_ssm_client()

  ssm.delete_parameter(Name = name)

  return True
