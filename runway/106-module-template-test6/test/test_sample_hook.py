from unittest import TestCase

from hooks import sampleHook
from test import fixture_json
from runway.cfngin import context, config
import os
cfngin_config = config.Config()
cfngin_config.namespace = 'dotcom-dev-3'

# Sample Test Hook serves as reference and should be removed when creating new module
class TestHook(TestCase):

    def test_AWS_DEFAULT_REGION_and_no_region_context(self):
        os.environ["AWS_DEFAULT_REGION"] =  "us-west-2"
        cfngin_context = context.Context(environment={'environment': 'dev'}, config=cfngin_config)
        unhooked = sampleHook.hook(None, context = cfngin_context)
        self.assertTrue(unhooked)
        del os.environ["AWS_DEFAULT_REGION"]

    def test_region_context_no_AWS_DEFAULT_REGION(self):
        cfngin_context = context.Context(environment={'region': 'us-west-2', 'environment': 'dev'},
                                  config=cfngin_config)
        unhooked = sampleHook.hook(None, context = cfngin_context)
        self.assertTrue(unhooked)

    def test_AWS_DEFAULT_REGION_matches_context_region(self):
        os.environ["AWS_DEFAULT_REGION"] =  "us-west-2"
        cfngin_context = context.Context(environment={'region': 'us-west-2', 'environment': 'dev'},
                                  config=cfngin_config)
        unhooked = sampleHook.hook(None, context = cfngin_context)
        self.assertTrue(unhooked)
        del os.environ["AWS_DEFAULT_REGION"]