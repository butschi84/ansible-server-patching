#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# PRTG Status list:
# 0=None
# 1=Unknown
# 2=Scanning
# 3=Up
# 4=Warning
# 5=Down
# 6=No Probe
# 7=Paused by User
# 8=Paused by Dependency
# 9=Paused by Schedule
# 10=Unusual
# 11=Not Licensed
# 12=Paused Until
# 13=Down Acknowledged
# 14=Down Partial

from ansible.module_utils.urls import *
from ansible.module_utils.basic import *
import re
import time
import xml.etree.ElementTree as ET
from ansible.module_utils.six.moves.urllib.parse import urlencode
DOCUMENTATION = '''
---
module: check_prtg
author: "Roman Hüsler (openzilla.ch)"
short_description: Check Monitoring Status of PRTG devices
description:
   - Observe Paessler PRTG devices by using its REST API
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
    required: false
  status:
    description:
      - Module will fail if sensor in prtg doesnt have the specified status (up, warning, down)
    required: false
  waitFor:
    description:
    - Module will wait for specified amounts of seconds until the host in prtg has the desired state. (default: 0)
    required: false
requirements: ["PRTG installation must be accessible from ansible client"]
'''

EXAMPLES = '''
- prtg:  prtg_url="https://prtg.example.com/" 
         api_user=ansible_api
         api_passhash=1234567890
         device_id=host.example.com
         status=up
         waitFor=0
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

def queryPrtgDevice(module, device_id):
    check_resp, check_info = api_call(module, '/api/table.json', {
                                        'content': 'devices', 'output': 'json', 'columns': 'objid,device,host,group,active,status,warnsens,downsens,upsens,totalsens', 'filter_objid': device_id})
    if(validate_response(module, check_info) != 200):
        module.fail_json(msg='API request failed')
    check_result = json.loads(check_resp.read())
    check_resp.close()

    # check to see if device exists
    if check_result['devices']:
        device = check_result['devices'][0]
        return device
    else:
        module.fail_json(msg='API request failed. No valid response',detail=check_result)

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
            status=dict(default='up', choices=['up', 'warning', 'down']),
            validate_certs=dict(default='yes', type='bool'),
            waitFor=dict(default=0, type='int',required=False),
        ),
        supports_check_mode=True
    )

    device_id = module.params['device_id']

    # prepare result
    device = queryPrtgDevice(module, device_id)
    result = {
        'dev_changed': False,
        'device_details': device,
        'msg': ''
    }
    
    # wait for desired result
    waited = 0
    while waited <= int(module.params['waitFor']):
        result['device_details'] = queryPrtgDevice(module, device_id)
        device = result['device_details']

        # setup some variables
        upsens = int(result['device_details']['upsens_raw'])
        totalsens = int(result['device_details']['totalsens_raw'])
        warnsens = int(result['device_details']['warnsens_raw'])
        downsens = int(result['device_details']['downsens_raw'])

        # calculate result
        if module.params['status'] == 'up':
            if int(device['status_raw']) == 3 and totalsens == upsens:
                result['msg'] = "device is up"
                module.exit_json(changed=result['dev_changed'], details=result)
            elif waited > int(module.params['waitFor']):
                result['msg'] = "device is not up or not all sensors are green"
                module.fail_json(changed=result['dev_changed'], details=result, msg=result['msg'])
            else:
                result['msg'] = ("device is not up or not all sensors are green after waiting " + str(waited) + " seconds")
                waited += 1
                time.sleep(1)
        elif module.params['status'] == 'down':
            if (int(device['status_raw']) != 3 and int(device['status_raw']) != 4) or totalsens!=upsens:
                result['msg'] = "device is down or some sensors are not green"
                module.exit_json(changed=result['dev_changed'], details=result)
            elif waited > int(module.params['waitFor']):
                result['msg'] = "device is not down. all sensors are green"
                module.fail_json(changed=result['dev_changed'], details=result, msg=result['msg'])
            else:
                result['msg'] = ("device is not down. all sensors are green after waiting " + str(waited) + " seconds")
                waited += 1
                time.sleep(1)
        elif module.params['status'] == 'warning':
            if int(device['status_raw']) == 4 or (downsens == 0 and warnsens > 0):
                result['msg'] = "device is in warning state"
                module.exit_json(changed=result['dev_changed'], details=result)
            elif waited > int(module.params['waitFor']):
                result['msg'] = "device is not in warning state"
                module.fail_json(changed=result['dev_changed'], details=result, msg=result['msg'])
            else:
                result['msg'] = ("device is not in warning state after waiting " + str(waited) + " seconds")
                waited += 1
                time.sleep(1)

    module.fail_json(changed=result['dev_changed'], details=result, msg=result['msg'])

# import module snippets
if __name__ == '__main__':
    main()
