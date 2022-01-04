#!/usr/bin/python
#
# roman huesler (opensight.ch) - github.com/butschi84
#
# Ansible Module "hyperv_action_state"
# - start or shutdown hyper-v vm's by "vmname"
#
# Parameters:
# - vmname:
#   name of vm to be started or shutdown (i.e. "vmname01")
# - state:
#   state of vm ("running", "stopped")
#
# ===================================================================

DOCUMENTATION = '''
---
module: hyperv_action_state
author: "roman hüsler (opensight.ch)"
short_description: shut down or start a hyper-v vm
description:
   - shutdown or start a hyper-v vm
options:
  vmname:
    description:
    - name of virtual machine
    required: true  
  state:
    description:
    - desired state ("running","stopped")
    required: true
'''

EXAMPLES = '''
# start vm01
- hyperv_action_shutdownvm:  
  vmname="vm01"
  state="running"
'''
