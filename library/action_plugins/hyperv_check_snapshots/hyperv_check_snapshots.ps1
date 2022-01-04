#!powershell
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

#Requires -Module Ansible.ModuleUtils.Legacy

$ErrorActionPreference = "Stop"

$params = Parse-Args -arguments $args -supports_check_mode $true
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false
$diff_mode = Get-AnsibleParam -obj $params -name "_ansible_diff" -type "bool" -default $false

$vmname = Get-AnsibleParam -obj $params -name "vmname" -type "str" -failifempty $true
$state  = Get-AnsibleParam -obj $params -name "state" -type "str" -default "absent" -validateset "absent","present"
$snapshotAgeYoungerThanMinutes = Get-AnsibleParam -obj $params -name "snapshotAgeYoungerThanMinutes" -type "str" -failifempty $false

# prepare output
$result = @{
    changed = $false
    snapshots = @()
    numSnapshots = $null
}

# get vm with the name specified
$vms = get-vm | select name
$vm = $vms | Where-Object { $_.name.toLower() -eq $vmname.toLower() }
if($vm -eq $null) {
    Fail-Json -obj $result -message "the specified vm could not be found on server"
}

# query snapshots of this vm
$snapshots = Get-VMSnapshot -VMName $vm[0].name | Sort-Object -Descending -Property creationTime

# check whether this vm has snapshots
$result = @{
    changed = $false
    numSnapshots = ($snapshots | measure).Count
    snapshots = @()
}
foreach($snapshot in $snapshots) {
    $result.snapshots += @{
        vmName = $snapshot.VMName
        creationTimeRaw = ([DateTimeOffset]$snapshot.creationTime).ToUnixTimeSeconds()
        creationTime = $snapshot.creationTime.tostring(“yyyy-MM-dd HH:mm:ss”)
        snapshotType = $snapshot.snapshotType
        snapshotAgeMinutes = [math]::Round((New-TimeSpan -Start $snapshot.creationTime -End (Get-Date)).TotalMinutes)
    }
}

switch($state) {
    # vm should have 1+ snapshots in order to succeed
    "present" {
        if($result.numSnapshots -gt 0) {
            if($snapshotAgeYoungerThanMinutes -ne $null){
                # get the youngest snapshot
                $youngestSnapshotAgeMinutes = [math]::Round((New-TimeSpan -Start $snapshots[0].creationTime -End (Get-Date)).TotalMinutes)
                if([int]$snapshotAgeYoungerThanMinutes -gt $youngestSnapshotAgeMinutes){
                    Exit-Json -obj $result -message ("vm has " + $result.numSnapshots + " snapshots. Youngest has age " + $youngestSnapshotAgeMinutes + " Minutes")
                }else{
                    Fail-Json -obj $result -message ("vm has snapshots. but newest one has age of " + $youngestSnapshotAgeMinutes + " minutes")
                }
            }else{
                Exit-Json -obj $result -message ("vm has " + $result.numSnapshots + " snapshots")
            }
        }else{
            Fail-Json -obj $result -message "vm has no snapshots"
        }
    }
    # vm should have 0 snapshots in order to succeed
    "absent" {
        if($result.numSnapshots -eq 0){
            Exit-Json -obj $result -message ("vm has no snapshots")
        }else{
            Fail-Json -obj $result -message ("vm has " + $result.numSnapshots + " snapshots")
        }
    }
    default {
        Fail-Json -obj $result -message ("unknown error / unknown state in module hyperv_check_snapshots")
    }
}
