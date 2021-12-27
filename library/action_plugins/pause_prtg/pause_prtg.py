#!/usr/bin/python
# -*- coding: utf-8 -*-

# roman huesler (opensight.ch) - github.com/butschi84
#
# Ansible Module "pause_prtg"
# - Pause or unpause monitoring for a prtg device
#
# ===================================================================
from ansible.module_utils.urls import *
from ansible.module_utils.basic import *
import re
import xml.etree.ElementTree as ET
from ansible.module_utils.six.moves.urllib.parse import urlencode
DOCUMENTATION = '''
---
module: pause_prtg
author: "roman hüsler (opensight.ch)"
short_description: Pause / Unpause monitoring of PRTG devices
description:
   - Pause / Unpause monitoring of Paessler PRTG devices using the REST API
options:
  api_user:
    description:
      - PRTG user for making API calls (can be local or domain user)
    required: true
  api_passhash:
    description:
      - Passhash of API user (see https://www.paessler.com/manuals/prtg/my_account_settings)
    required: true
  prtg_url:
    description:
      - The base URL of your PRTG installation (e.g. https://prtg.example.com/)
    required: true
  device_id:
    description:
      - ID of PRTG device (one of device_name or device_id required)
    required: true
  status:
    description:
      - Whether the device should be paused or not
    required: true
    choices: [ "paused", "running" ]
    default: paused
requirements: ["PRTG installation must be accessible from ansible client"]
'''

EXAMPLES = '''
- prtg:  prtg_url="https://prtg.example.com/" 
         api_user=ansible_api
         api_passhash=1234567890
         device_id=1027         
         status=paused
'''

try:
    import json
except ImportError:
    import simplejson as json

# ===========================================
# PRTG helper methods
#


def api_call(module, path, params):

    # determine URL for PRTG API
    if (module.params['prtg_url']).endswith('/'):
        url = (module.params['prtg_url']).rstrip('/') + path
    else:
        url = module.params['prtg_url'] + path

    # build parameters
    params['username'] = module.params['api_user']
    params['passhash'] = module.params['api_passhash']

    data = urlencode(params)

    url = url + '?' + data

    return fetch_url(module, url, method='GET')


def validate_response(module, resp_info):

    if resp_info['status']:
        if resp_info['status'] == 401:
            module.fail_json(msg='Invalid API credentials')
        elif resp_info['status'] == 404:
            module.fail_json(msg='Invalid API URL')
        elif resp_info['status'] == 400:
            module.fail_json(
                msg='The API call could not be completed successfully')
        elif resp_info['status'] == 200:
            return 200
        elif resp_info['status'] == 302:
            return 302
    else:
        module.fail_json(msg='Unable to reach API server')

    return 0


def pause_device(module, device_id, paused):
    # set paused var for api_call
    if paused:
        pause_action = 0
    else:
        pause_action = 1

    # make the API call
    resp, info = api_call(module, '/api/pause.htm',
                          {'id': device_id, 'pausemsg': 'paused by ansible', 'action': pause_action})
    if(validate_response(module, info) != 200):
        module.fail_json(msg='Failed to pause device')
    resp.close()

    return True


# ===========================================
# Module execution
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            api_user=dict(required=True),
            api_passhash=dict(required=True),
            prtg_url=dict(required=True),
            device_id=dict(required=True),
            status=dict(default='present', choices=['paused', 'running'])
        ),
        supports_check_mode=True
    )

    device_id = module.params['device_id']

    # do an API call and get results
    check_resp, check_info = api_call(module, '/api/table.json', {
        'content': 'devices', 'output': 'json', 'columns': 'objid,device,host,group,active,status'})
    if(validate_response(module, check_info) != 200):
        module.fail_json(msg='API request failed')
    check_result = json.loads(check_resp.read())
    check_resp.close()

    # check to see if device exists
    if not check_result or len(check_result['devices']) == 0:
        module.fail_json(msg='failed to query prtg devices',
                         detail=check_result)

    # find specified device
    device = None
    for dvc in check_result['devices']:
        if int(dvc['objid']) == int(device_id):
            device = dvc

    # check wether device has been found
    if device is None:
        module.fail_json(
            msg='API request failed. No valid response', detail=check_result)
        return

    # setup changed variable
    dev_changed = False

    # pause or unpause the device
    if module.params['status'] == "running" and int(device['status_raw']) == 7:
        if not module.check_mode:
            pause_device(module, device_id, paused=False)
        dev_changed = True
        module.exit_json(changed=dev_changed,
                         action="unpause device", device_before=device)
    elif module.params['status'] == "paused" and int(device['status_raw']) != 7:
        if not module.check_mode:
            pause_device(module, device_id, paused=True)
        dev_changed = True
        module.exit_json(changed=dev_changed,
                         action="pause device", device_before=device)
    else:
        module.exit_json(changed=dev_changed, action="none",
                         device_before=device)


# import module snippets

if __name__ == '__main__':
    main()
