#!/usr/bin/python
#
# roman huesler (opensight.ch) - github.com/butschi84
#
# Ansible Module "hyperv_action_createsnapshot"
# - Create a snapshot for a hyper-v vm by using "vmname"
#
# Parameters:
# - vmname:
#   name of vm (i.e. "vmname01")
# - snapshotName:
#   not required. default value is "ansible_hyperv_action_createsnapshot"
#
# ===================================================================
DOCUMENTATION = '''
---
module: hyperv_action_createsnapshot
author: "roman hüsler (opensight.ch)"
short_description: create a new snapshot of a hyperv vm
description:
   - create a new snapshot of a hyperv vm
options:
  vmname:
    description:
    - name of virtual machine
    required: true  
  snapshotName:
    description:
    - name of snapshot, that will be created
    required: false
'''

EXAMPLES = '''
- hyperv_action_createsnapshot:  
    vmname="vm01"
    snapshotName="test" 
'''
