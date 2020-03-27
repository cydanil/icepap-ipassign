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
can be set, and a more advanced `NetworkWindow` in which ip setting can also be configured.  
By default, `HostnameWindow` is displayed.  
The `Advanced` push-button allows to switch to the `NetworkWindow` view.

IP addresses within `NetworkWindow` are validated using `ipassing.utils.validate_ip_addr`.

A log of the traffic on the network and actions within ipassign can be viewed in `LogWindow`.
This window contains a read-only text field that, when displayed refreshes automatically.  
From the log window, it is possible to save these to file.

[gui_workflow]: workflow.png "Image describing a user's workflow"
