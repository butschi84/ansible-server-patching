# ansible - server patching framework

:warning: **Use at your own risk** :warning:

This repository will contain ansible playbooks and custom modules helpful to patch windows and linux systems. You will also be able to run checks and actions on third party systems like prtg, hyper-v, veeam and so on.

## Features
These are the current Features of the patching framework.

* Hyper-V
  * Start a VM
  * Stop a VM
  * Check if a VM has a snapshot younger than x-Minutes  
  * Check if a VM has no snapshots
  * Create a snapshot for a VM
* PRTG
  * Pause monitoring of a PRTG Device
  * Resume monitoring of a PRTG Device
  * Check current monitoring status of a PRTG Device

# Contents
- [ansible - server patching framework](#ansible---server-patching-framework)
  - [Features](#features)
- [Contents](#contents)
- [Setup Framework](#setup-framework)
  - [Setup credentials](#setup-credentials)
  - [Module - PRTG](#module---prtg)
  - [Module - HYPERV](#module---hyperv)
- [Playbooks](#playbooks)
  - [PRTG](#prtg)
    - [check-readyness.yml](#check-readynessyml)
    - [pause-monitoring.yml](#pause-monitoringyml)
    - [resume-monitoring.yml](#resume-monitoringyml)
  - [Hyper-V](#hyper-v)
    - [hyperv-check-snapshots.yml](#hyperv-check-snapshotsyml)
    - [hyperv-action-createsnapshot.yml](#hyperv-action-createsnapshotyml)
    - [hyperv-check-nosnapshots.yml](#hyperv-check-nosnapshotsyml)
- [Custom Modules](#custom-modules)
  - [PRTG](#prtg-1)
    - [check\_prtg](#check_prtg)
    - [pause\_prtg](#pause_prtg)
  - [Hyper-V](#hyper-v-1)
    - [hyperv\_check\_snapshots](#hyperv_check_snapshots)
    - [hyperv\_action\_createsnapshot](#hyperv_action_createsnapshot)
    - [hyperv\_action\_state](#hyperv_action_state)

# Setup Framework<a name="Setup"></a>

Once you have downloaded the repository, you have to configure some parameters so the framework is able to connect to the environment.

## Setup credentials<a name="SetupCredentials"></a>

The credential store contains the passwords to connect to your linux and windows systems.

Setup your vault using the following procedure:

1. Save vault password to file
```
echo MyPassword > ~/vault-password.txt
```

2. create ansible vault
  
```
# windows - create vault
ansible-vault create ./environments/prod/group_vars/windows_servers/secrets.yml
windows_admin_username: "myDomain\\myWindowsUser"
windows_admin_password: "myWindowsPassword"

# linux - create vault
ansible-vault create ./environments/prod/group_vars/linux_servers/secrets.yml
linux_admin_username: "myLinuxUser"
linux_admin_password: "myLinuxPassword"
```

3. edit inventory file

edit the host file as desired
```
vi ./environments/prod/inventory.yml
```

## Module - PRTG<a name="SetupModulePRTG"></a>

If you plan to use the 'prtg' module you have to setup the following

1. add prtg parameters to your vault

```
ansible-vault create ./environments/prod/group_vars/all/secrets_prtg.yml
```

2. append your prtg connection parameters
```
# parameters for module 'prtg'
prtg_api_url: 172.20.0.91
prtg_api_user: exampleUser
prtg_api_passhash: 111111111
```

3. specify prtg_device_id

Add the prtg_device_id for each of the hosts. example file:
```
environments/prod/host_vars/linux_example_server.yml
```
You can find the PRTG device id in your prtg web interface.

![prtg readyness](documentation/check_readyness.png "PRTG Patch Readyness Check")

The password hash has to be taken from PRTG.

## Module - HYPERV<a name="SetupModuleHyperv"></a>

If you plan to use the 'hyperv' module you have to setup the following:

1. add hyperv parameters to your vault

```
ansible-vault create ./environments/prod/group_vars/all/secrets_hyperv.yml
```
2. append your prtg connection parameters
```
# parameters for module 'hyperv'
hyperv_host: 172.20.0.91
hyperv_admin_username: administrator
hyperv_admin_password: secret
```

3. specify hyperv_vmname

Add the hyperv_vmname for each of the hosts. example file:
```
environments/prod/host_vars/linux_example_server.yml
```

# Playbooks<a name="Playbooks"></a>
This section contains some examples of playbooks that show the usage of the custom modules in the repository.

## PRTG<a name="PlaybooksPRTG"></a>
Playbooks useful to run checks on you PRTG monitoring, pause sensors, resume sensors. 

> These playbooks use the 'prtg' module of this repository.
> So make sure you have setup the prtg module correctly as specified in the 'Setup Framework' section.

### check-readyness.yml<a name="PlaybooksPRTGCheckReadyness"></a>
> playbooks/prtg/check-readyness.yml

Example Playbook to check the current status of a device / system in prtg.
Each host will be checked in prtg by using its specific device id. 

```
# Usage:
ansible-playbook playbooks/prtg/check-readyness.yml --limit example_server
```

### pause-monitoring.yml<a name="PlaybooksPRTGPause"></a>
> playbooks/prtg/pause-monitoring.yml

Example Playbook to pause monitoring of a device / system in prtg.

```
# Usage:
ansible-playbook playbooks/prtg/pause-monitoring.yml --limit example_server
```
### resume-monitoring.yml<a name="PlaybooksPRTGResume"></a>
> playbooks/prtg/resume-monitoring.yml

Example Playbook to resume monitoring of a device / system in prtg.

```
# Usage:
ansible-playbook playbooks/prtg/resume-monitoring.yml --limit example_server
```

## Hyper-V<a name="PlaybooksHyperv"></a>
Playbooks useful to run checks on your Hyper-V Host, check snapshots and age, create snapshots, delete snapshots. 

> These playbooks use the 'hyperv' module of this repository.
> So make sure you have setup the hyperv module correctly as specified in the 'Setup Framework' section.

### hyperv-check-snapshots.yml<a name="PlaybooksHypervCheck"></a>
> playbooks/hyperv/hyperv-check-snapshots.yml

Example Playbook to check wether a hyper-v vm has a snapshot and age is younger than 1 day.

```
# Usage:
ansible-playbook playbooks/hyperv/hyperv-check-snapshots.yml --limit example_server
```
### hyperv-action-createsnapshot.yml<a name="PlaybooksHypervCreate"></a>
> playbooks/hyperv/hyperv-action-createsnapshot.yml

Example Playbook to show snapshot creation for a hyper-v vm.

```
# Usage:
ansible-playbook playbooks/hyperv/hyperv-action-createsnapshot.yml --limit example_server
```
### hyperv-check-nosnapshots.yml<a name="PlaybooksHypervCheckNoS"></a>
> playbooks/hyperv/hyperv-check-nosnapshots.yml

Example Playbook to check wether a hyper-v vm has no snapshot.

```
# Usage:
ansible-playbook playbooks/hyperv/hyperv-check-nosnapshots.yml --limit example_server
```

# Custom Modules<a name="CustomModules"></a>
This repository contains custom modules for ansible so you are able to connect to 3rd party systems, run checks and actions.

## PRTG<a name="CustomModulesPRTG"></a>
Modules for Paessler PRTG monitoring.

### check_prtg<a name="CustomModulesPRTGCheck"></a>
> library/action_plugins/check_prtg

Custom module that can be used to check the status of a device in prtg monitoring (up, warning, down).

* Module should be executed on a linux system that has connectivity (http) to the prtg server.
* For Example Usage see playbook [check-readyness.yml](#PlaybooksPRTGCheckReadyness)

**Parameters**
* **api_user**:
  PRTG user for making API calls (can be local or domain user i.e. "prtgadmin")
* **api_passhash**:
  Passhash from PRTG for API access (i.e. 1234512345)
* **prtg_url**:
  Address of PRTG Server (i.e. "192.168.2.100") 
* **device_id**:
  Id of device in PRTG that should be checked (i.e. "1022")
* **status**:
  Desired Status of device in PRTG (i.e. "up", "warning", "down"). Default: "up"
* **waitFor**:
  If device does not have the desired status in PRTG, how many seconds should we wait (default: 0)

### pause_prtg<a name="CustomModulesPRTGPause"></a>
> library/action_plugins/pause_prtg

Custom module that can be used to pause or resume monitoring of a device in prtg.

* Module should be executed on a linux system that has connectivity (http) to the prtg server.
* For Example Usage see playbook [pause-monitoring.yml](#PlaybooksPRTGPause)
* For Example Usage see playbook [resume-monitoring.yml](#PlaybooksPRTGResume)

**Parameters**
* **api_user**:
  PRTG user for making API calls (can be local or domain user i.e. "prtgadmin")
* **api_passhash**:
  Passhash from PRTG for API access (i.e. 1234512345)
* **prtg_url**:
  Address of PRTG Server (i.e. "192.168.2.100") 
* **device_id**:
  Id of device in PRTG that should be checked (i.e. "1022")
* **status**:
  Desired Status of device in PRTG after the action is taken (i.e. "paused", "running"). Default: "paused"

## Hyper-V<a name="CustomModulesHyperV"></a>
Modules for checking-, creating- and deleting snapshots on Microsoft Hyper-V Hypervisors.

### hyperv_check_snapshots<a name="CustomModulesHyperVCheck"></a>
> library/action_plugins/hyperv_check_snapshots

Custom module that can be used to check wether a hyper-v vm has a snapshot and also age of the snapshot.

* Module is a powershell script should be executed on a windows hyper-v host
* For Example Usage see playbook [hyperv-check-snapshots.yml](#PlaybooksHypervCheck)

**Parameters**
* **vmname**:<br />
  name of hyper-v vm that should be checked (i.e. "myvm01")
* **state**:<br />
  state of snapshot should be: "absent" or "present"
* **snapshotAgeYoungerThanMinutes**:<br />
  max snapshot age in minutes if "present" was specified
### hyperv_action_createsnapshot<a name="CustomModulesHypervCreate"></a>
> library/action_plugins/hyperv_action_createsnapshot

Custom module that can be used to create a new snapshot for a hyper-v vm

* Module is a powershell script should be executed on a windows hyper-v host
* For Example Usage see playbook [hyperv-action-createsnapshot.yml](#PlaybooksHypervCreate)

**Parameters**
* **vmname**:<br />
  name of hyper-v vm where snapshot should be created (i.e. "myvm01")
* **snapshotName**:<br />
  (optional) name of snapshot that should be created
### hyperv_action_state<a name="CustomModulesHyperVActionState"></a>
> library/action_plugins/hyperv_action_state

Custom module that can be used to start or shutdown a hyper-v vm.

* Module is a powershell script should be executed on a windows hyper-v host

**Parameters**
* **vmname**:<br />
  name of hyper-v vm that should be started or shutdown (i.e. "myvm01")
* **state**:<br />
  state of vm should be: "running" or "stopped"

