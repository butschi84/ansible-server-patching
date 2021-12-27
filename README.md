# ansible - server patching framework

**Use at your own risk**

This repository will contain ansible playbooks and custom modules helpful to patch windows and linux systems. You will also be able to run checks and actions on third party systems like prtg, hyper-v, veeam and so on.

# Contents
- [ansible - server patching framework](#ansible---server-patching-framework)
- [Contents](#contents)
- [Setup Framework<a name="Setup"></a>](#setup-framework)
  - [Setup credentials<a name="SetupCredentials"></a>](#setup-credentials)
  - [Module - PRTG<a name="SetupModulePRTG"></a>](#module---prtg)
- [Playbooks<a name="Playbooks"></a>](#playbooks)
  - [PRTG<a name="PlaybooksPRTG"></a>](#prtg)
    - [check-readyness.yml<a name="PlaybooksPRTGCheckReadyness"></a>](#check-readynessyml)
    - [pause-monitoring.yml<a name="PlaybooksPRTGPause"></a>](#pause-monitoringyml)
    - [resume-monitoring.yml<a name="PlaybooksPRTGResume"></a>](#resume-monitoringyml)
- [Custom Modules<a name="CustomModules"></a>](#custom-modules)
  - [PRTG<a name="CustomModulesPRTG"></a>](#prtg-1)
    - [check_prtg<a name="CustomModulesPRTGCheck"></a>](#check_prtg)
    - [pause_prtg<a name="CustomModulesPRTGPause"></a>](#pause_prtg)

# Setup Framework<a name="Setup"></a>

Once you have downloaded the repository, you have to configure some parameters so the framework is able to connect to the environment.

## Setup credentials<a name="SetupCredentials"></a>

The credential store contains the passwords to connect to your linux and windows systems.

Setup your vault using the following procedure:

1. Save vault password to file
```
echo MyPassword > vault-password.txt
```

2. create ansible vault
  
```
# create vault
ansible-vault create ./environments/prod/group_vars/all/vault.yml
```

3. enter the following information

```
# Connection parameters
windows_admin_username: "myDomain\\myWindowsUser"
windows_admin_password: "myWindowsPassword"
linux_admin_username: "myLinuxUser"
linux_admin_password: "myLinuxPassword"
```

4. edit hosts file

edit the host file as desired
```
vi ./environments/prod/hosts
```

## Module - PRTG<a name="SetupModulePRTG"></a>

If you plan to use the 'prtg' module you have to setup the following

1. add prtg parameters to your vault

```
ansible-vault edit ./environments/prod/group_vars/all/vault.yml
```
2. append your prtg connection parameters
```
# parameters for module 'prtg'
module_prtg_server_address: 172.20.0.91
module_prtg_api_username: exampleUser
module_prtg_api_passhash: 111111111
```
3. edit environments/prod/group_vars/all/hosts

Add the prtg_device_id to each of the hosts you want to use with the prtg module like so:
```
[windows_servers]
example_server ansible_host=172.20.0.91 prtg_device_id=1027
```
You can find the PRTG device id in your prtg web interface.

![prtg readyness](documentation/check_readyness.png "PRTG Patch Readyness Check")

The password hash has to be taken from PRTG.

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

# Custom Modules<a name="CustomModules"></a>
This repository contains custom modules for ansible so you are able to connect to 3rd party systems, run checks and actions.

## PRTG<a name="CustomModulesPRTG"></a>
Modules for Paessler PRTG monitoring.

### check_prtg<a name="CustomModulesPRTGCheck"></a>
> library/action_plugins/check_prtg

Custom module that can be used to check the status of a device in prtg monitoring.

* Module should be executed on a linux system that has connectivity (http) to the prtg server.
* For Example Usage see playbook [check-readyness.yml](#PlaybooksPRTGCheckReadyness)

### pause_prtg<a name="CustomModulesPRTGPause"></a>
> library/action_plugins/pause_prtg

Custom module that can be used to pause or resume monitoring of a device in prtg.

* Module should be executed on a linux system that has connectivity (http) to the prtg server.
* For Example Usage see playbook [pause-monitoring.yml](#PlaybooksPRTGPause)
* For Example Usage see playbook [resume-monitoring.yml](#PlaybooksPRTGResume)