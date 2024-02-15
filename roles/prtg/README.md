the prtg role lets you run certain tasks for each device against prtg monitoring:

* check_monitoring<br />
  check if monitoring is green for device
* pause_monitoring<br />
  pause monitoring for device
* resume_monitoring<br />
  resume monitoring for device

# Prerequisites

- `prtg_device_id` variable has to be specified for each device
- following variables have to be also specified globally `prtg_api_user`, `prtg_api_passhash`, `prtg_api_url`