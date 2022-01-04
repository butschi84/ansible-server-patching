#!powershell
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

#Requires -Module Ansible.ModuleUtils.Legacy

$ErrorActionPreference = "Stop"

$params = Parse-Args -arguments $args -supports_check_mode $true
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false
$diff_mode = Get-AnsibleParam -obj $params -name "_ansible_diff" -type "bool" -default $false

$vmname = Get-AnsibleParam -obj $params -name "vmname" -type "str" -failifempty $true
$snapshotName = Get-AnsibleParam -obj $params -name "snapshotName" -type "str" -failifempty $false -default "ansible_hyperv_action_createsnapshot"

# prepare output
$result = @{
    changed = $false
    snapshots = @()
    numSnapshots = $null
    action = "create a new snapshot"
}

# get vm with the name specified
$vms = get-vm | select name
$vm = $vms | Where-Object { $_.name.toLower() -eq $vmname.toLower() }
if($vm -eq $null) {
    Fail-Json -obj $result -message "the specified vm could not be found on server"
}

if($check_mode -ne $true)
{
    Checkpoint-VM -Name $vm[0].name -SnapshotName $snapshotName 
}
$result.changed = $true

# query snapshots of this vm
$snapshots = Get-VMSnapshot -VMName $vm[0].name | Sort-Object -Descending -Property creationTime

# check whether this vm has snapshots
$result.numSnapshots = ($snapshots | measure).Count 
foreach($snapshot in $snapshots) {
    $result.snapshots += @{
        vmName = $snapshot.VMName
        creationTimeRaw = ([DateTimeOffset]$snapshot.creationTime).ToUnixTimeSeconds()
        creationTime = $snapshot.creationTime.tostring(“yyyy-MM-dd HH:mm:ss”)
        snapshotType = $snapshot.snapshotType
        snapshotAgeMinutes = [math]::Round((New-TimeSpan -Start $snapshot.creationTime -End (Get-Date)).TotalMinutes)
    }
}

Exit-Json -obj $result -message ("vm has " + $result.numSnapshots + " snapshots")
