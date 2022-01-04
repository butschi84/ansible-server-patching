#!/usr/bin/python
#
# roman huesler (opensight.ch) - github.com/butschi84
#
# Ansible Module "hyperv_check_snapshot"
# - Check wether hyper-v vm has a snapshot by "vmname"
#
# Parameters:
# - vmname:
#   name of vm to be checked (i.e. "vmname01")
# - state:
#   state of snapshot ("absent", "present")
# - snapshotAgeYoungerThanMinutes:
#   max snapshot age in minutes if "present" was specified
#
# ===================================================================

DOCUMENTATION = '''
---
module: hyperv_check_snapshots
author: "roman hüsler (opensight.ch)"
short_description: Check if VM has snapshots on hyperv server
description:
   - Check if VM has snapshots on hyperv server
options:
   vmname:
     description:
     - i.e. myvm01
     required: true
   state:
     description:
     - absent => [default] - succeed when vm has no snapshots
     - present =>  succeed when vm has one or more snapshots
    required: false
  snapshotAgeYoungerThanMinutes:
    description:
    - max snapshot age in minutes if "present" was specified
    - if parameter is skipped then snapshot age is not checked
    required: false
'''

EXAMPLES = '''
- hyperv_check_snapshots:  
         name="Software" 
         state=present
         value=1234567890
'''
