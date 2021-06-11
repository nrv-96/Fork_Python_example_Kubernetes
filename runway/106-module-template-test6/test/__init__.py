''' Holds common functions for test '''
import json
import os
import sys
from os import environ
from collections import namedtuple

environ["AWS_DEFAULT_REGION"] = 'us-west-2'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def fixture_json(filename):
  ''' Loads a file as json from the fixtures folder '''
  full_path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
  with open(full_path) as json_fixture_file:
    return json.loads(json_fixture_file.read())

def namedtuple_dict(dictionary):
  return namedtuple('TestDict', dictionary.keys())(**dictionary)