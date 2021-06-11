"""utils helper functions"""
"""Please update the macros in stacker-shared-libraries/macros/macros.jinja whenever an update is made to the macro functions in this file"""
"""https://stash1-tools.swacorp.com/projects/CCPLAT/repos/stacker-shared-libraries/browse/libs/macros/macros.jinja"""

def format_name(name):
    """format name"""
    for special_char in ['\\','`','*','_','{','}','[',']','(',')','>','#','+','-','.','!','$','\'','/','^','@', ' ']:
        if special_char in name:
            name = name.replace(special_char,'')
    return name.capitalize()[:91]


def test_dict_for_bool(key, dictionary):
  resp = False
  val = dictionary.get(key, False)
  if isinstance(val, bool):
    resp = val
  elif isinstance(val, str):
    if val.upper() == 'TRUE':
      resp = True
    else:
      resp = False
  return resp