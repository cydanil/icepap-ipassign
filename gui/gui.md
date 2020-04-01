# IPAssign GUI

## Workflow

The usage is of the ipassign application is as follows:

![alt text][gui_workflow]

## Implementation

The gui is implemented using PyQt5.  

There are four windows.  
`MainWindow` is the application entry point, on which a list of discovered
icepaps is displayed.  

When launched, the application will send a discovery packet to find devices.
This action can be repeated by clicking `Refresh`.
Clicking on an entry in the list will display its properties.

There are two properties windows, a simpler `HostnameWindow` where the hostname
can be set, and a more advanced `NetworkWindow` in which ip setting can also be
configured.
By default, `HostnameWindow` is displayed.  
The `Advanced` push-button allows to switch to the `NetworkWindow` view.

A log of the traffic on the network and actions within ipassign can be viewed
in `LogWindow`.
This window contains a read-only text field that, when displayed refreshes
automatically.  
From the log window, it is possible to save these to file.

## MainWindow

Results of the discovery are sorted by hostname in the central list.

## HostnameWindow

HostnameWindow only allows the setting of a device's hostname.  
Setting the hostname is the most common operation, and is ipassign's default
mode of operation.

The hostname is validated with respect to RFC 1123, section 2.1. If the
hostname is not valid, the `Apply` button is disabled.


## NetworkWindow

NetworkWindow allows the setting of all of a device's network settings.

These are Hostname, IP settings, and whether to apply these settings
dynamically, to write them to flash, or reboot.

Alternatively, it is also possible to query the DNS and set these as values
to apply.

The configuration given at the moment of drawing the window is kept
within `self._config`. The new configuration will only be created when
`Apply` is clicked.

The `Reset` button resets the fields with the values previously obtained from
the device (passed to the window upon drawing), that is stored in `self._config`.

Within `NetworkWindow`, IP address fields are first validated using
`ipassing.utils.validate_ip_addr`. Then, they are verified to be in range of
one another against the netmask.

As with `HostnameWindow`, the hostname is validated against RFC 1123.

If any field is invalid, `Apply` will be disabled.

## Networking

All the networking is handled by `networking.NetworkInterface`. This object has
the two methods `do_discovery` and `send_configuration`.


[gui_workflow]: workflow.png "Image describing a user's workflow"