#!powershell
#
# roman huesler (opensight.ch) - github.com/butschi84
#
# Ansible Module "hyperv_action_state"
# - start or shutdown hyper-v vm's by "vmname"
#
# Parameters:
# - vmname:
#   name of vm to be started or shutdown (i.e. "vmname01")
#   required
# - state: 
#   state of vm ("running", "stopped")
#   required
#   
# ===================================================================

#Requires -Module Ansible.ModuleUtils.Legacy

$ErrorActionPreference = "Stop"

$params = Parse-Args -arguments $args -supports_check_mode $true
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false
$diff_mode = Get-AnsibleParam -obj $params -name "_ansible_diff" -type "bool" -default $false

$vmname = Get-AnsibleParam -obj $params -name "vmname" -type "str" -failifempty $true
$state  = Get-AnsibleParam -obj $params -name "state" -type "str" -validateset "running","stopped" -failifempty $true

# prepare output
$result = @{
    changed = $false
    action = "no action"
}

# get vm with the name specified
$vms = get-vm | select name,state
$vm = $vms | Where-Object { $_.name.toLower() -eq $vmname.toLower() }
if($vm -eq $null) {
    Fail-Json -obj $result -message "the specified vm could not be found on server"
}

switch($state) {
    "running" {
        if($vm[0].state -eq "Running") {
            $result.action = ("no action required. vm is already running. state: " + $vm[0].state)
        }else{
            if($check_mode -ne $true) {
                Start-VM -Name $vmname
            }
            $result.action = "start vm"
            $result.changed = $true
        }
    }
    "stopped" {
        if($vm[0].state -eq "Running") {
            if($check_mode -ne $true) {
                Stop-VM -Name $vmname
            }
            $result.action = "stop vm"
            $result.changed = $true
        }else{
            $result.action = ("no action required. vm is already stopped. state: " + $vm[0].state)
        }
    }
}

Exit-Json -obj $result
