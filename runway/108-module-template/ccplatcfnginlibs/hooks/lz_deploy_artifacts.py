"""
Hook used to deploy artifacts using the Landing Zone deployment engine

Usage - Add this hook format to the stacker template:

pre_build:
  - path: libs.hooks.lz_deploy_artifacts.hook
    required: true
    enabled: true
    args:
      s3_prefix: theprefix
      artifacts:
        - artifacts/artifact1.zip
        - artifacts/artifact2.zip
      timeout: 300

  s3_prefix (required) - The prefix used when uploading the artifact to the s3 bucket
  artifacts (required) - The path to one or more artifacts to be deployed
  timeout (optional) - The timeout (in seconds) before the the hook times out and the
                       deployment is marked as failed. Default is 900 (15 minutes)
"""

from ccplatcfnginlibs.helpers.lz_deployer import deploy_artifacts
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER

import traceback
import sys

def hook(provider, context, **kwargs):
    """ Hook that deploys the artifact(s) """
    try:
      LOGGER.info(f'Running hook for module: {str(context.environment["module_name"])}')
      artifacts = kwargs.get("artifacts")
      s3_prefix = kwargs.get("s3_prefix")
      timeout = kwargs.get("timeout")
      region = context.environment.get("region")
      env = context.environment.get("environment")

      response = False
      if artifacts:
          if timeout:
              response = deploy_artifacts(
                  artifacts, s3_prefix, region, env, timeout=int(timeout)
              )
          else:
              response = deploy_artifacts(artifacts, s3_prefix, region, env)

      return response
    except BaseException as error:
      LOGGER.error(f'Hook failed for module: {str(context.environment["module_name"])}')
      LOGGER.error(f'{str(context.environment["module_name"])}: {"".join(traceback.TracebackException.from_exception(error).format())}')
      raise error.with_traceback(sys.exc_info()[2])