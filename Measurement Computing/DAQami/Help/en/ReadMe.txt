=====================================================================
                        DAQami(tm) Version 4.2.1 Software ReadMe
                          Measurement Computing Corporation
======================================================================

1. Introduction
2. Installation
3. Getting Started
4. New Features
5. Support and Contact Information
6. Known Issues
7. Fixed Issues


================
1. Introduction
================
DAQami is an out-of-the-box data acquisition software companion for 
acquiring, viewing, logging, and generating analog/temperature, digital, and 
counter data with supported Measurement Computing data acquisition devices. 

Configure the device and the channels to use as the data source, 
run an acquisition, and view the data on any combination of Scalar, 
Strip, and Block displays. Data from selected channels can be logged to TDMS files
for later review, and can be exported to a .csv file for further analysis. You can
also save your device, channel, sample rate, trigger, and display settings 
to a configuration file for later reuse.


=======================
2. Installation
=======================
IMPORTANT: Install DAQami before connecting your supported MCC DAQ
device.

The DAQami installation includes a self-extracting installer file,
DAQami.exe. 


=======================
3. Getting Started
=======================
Once you install the DAQami software, connect your device and let
the driver files load. After the drivers are loaded, launch DAQami. 


=============================
4. New Features
=============================
Version 4.2.1
* Resolved Auto Export issue when running consecutive, short acquisitions
* Resolved error that occurred after logging for short period (an hour or less) at low sample rates (10 S/s - 1000 S/s)
* Resolved memory leak related to the strip and block charts when performing long duration acquisitions
* Improved performance during TDMS file writing


Version 4.2.0
* Support for USB-1808 Series devices, including synchronous I/O 
  operations (composite operations)
* New options when exporting data to .csv files to specify the decimal 
  format character, column separator character, and whether to use or
  not use double quotation marks around text values
* Maximum channel name length increased from 10 characters to 25 characters
* German and Chinese language support

Version 4.1.0
* German and Chinese language support
* Resolved localization issues when logging to TDMS file format 

Version 4.0.0
* Log a virtually unlimited number of samples per channel
* Multiple device support
* Save updated display settings to an existing data file
* Show digital bit values as LEDs on Scalar display
* TDMS file support

Version 3.0.1
* German language support
* Fix for issue 584557

Version 3.0
* Output display type for analog, digital, and counter signal types
* Open thermocouple detection
* Analog hardware triggering
* Ability to rearrange the channel order on a display
* Ability to add one or more cursors to a live acquisition
* Minimum, maximum, and average values added to Scalar display
* 30-day evaluation; data logging and export disabled after 30 days 
  without purchase


Version 2.1 
* Support for mixed-signal types (HW and SW paced) on the same display.
* Improved timestamping of acquired data.
* Chinese language support


=========================================
5. Support and Contact Information 
==========================================
Contact Measurement Computing for technical support.

For US customers, please contact MCC at:

Measurement Computing
10 Commerce Way
Norton, MA 02766
Phone: (508) 946-5100
www.mccdaq.com
info@mccdaq.com

For customers outside of the US, please contact your local sales office:

www.mccdaq.com/distributors.


=========================================
6. Known Issues
=========================================

-------------
Analog Output
-------------

|579129|
If there is at least one activated hardware-paced analog output channel, 
changing the slider control for another analog output channel causes a glitch
in all other AO channels (both hardware and software-paced).
There is currently no known work-around for this issue.

–––––––––––––
Configuration
––––––––––––-

|473375|
Some supported devices require some configuration options to be set 
with InstaCal:

* E-1608, E-DIO24, E-TC, TC-32: configure the connection code, alarms, and manual 
  network settings (IP address and so on) with InstaCal before running DAQami.  
  DAQami can communicate with any device whose connection code is set
  to "0" in InstaCal, regardless of the code entered in DAQami.

* USB-TEMP, USB-TEMP-AI, USB-5203: Configure RTD, thermistor, and 
  semiconductor measurements with InstaCal before running DAQami.
  
 |612016|
 Auto Configuration locks up when using a USB-TC-AI for the first time.
 
 When adding a USB-TEMP-AI using an Auto Configuration for the first time 
 after running DAQami, the configuration locks up.
 
 Workaround: Close DAQami, disconnect and reconnect the USB cable on the USB-TEMP-AI, 
 and re-launch DAQami.

–––––-------
Data Logging
–––––-------

|405216|
DAQami does not check the amount of disk space available during
acquisition. 

Workaround: Before you run an acquisition involving a large number 
of samples, check to make sure you have enough disk space.

–––––––––––––
Execution
––––––––––––-

|621259|
If a DAQami acquisition is stopped by opening another MCC application -- such as Instacal, 
a Universal Library-based application, or TracerDAQ(R) -- DAQami does not notify the user 
that the acquisition has stopped.

If one of these applications is started during an acquisition and then closed, the DAQami
acquisition stops, but there is no error and the status remains running. 

Workaround: Save the configuration, close DAQami and the other application, and then 
re-launch DAQami and run the acquisition again.

-----------------------------------
Concurrent Input and Output Scans
-----------------------------------

|611365|
Devices configured for input scan and another for output scan
results in delayed output signal at 1 kS/s and below.

If one device is configured for an input scan and another for an output scan, 
no output signal is evident at the beginning of the acquisition. For input scans running 
at 1 kS/s, the output does not begin to change until about 15 ms to 70 ms (it varies from 
scan to scan. Output scans were configured for single channel and 1 Hz waveform.

This also occurs with a single device installed and scanning both input and output. 

–––––––-
Hardware
–––––––-

|480626|
miniLAB 1008 can only use DIO0 as trigger channel regardless of
the InstaCal setting.

Workaround: Selecting a trigger source other than DIO0 in InstaCal
is ignored in DAQami.

-------------------
Hardware Triggering
-------------------

|611738|
A hardware trigger using two devices is sometimes off by 25 ms to 75 ms between devices 
running at 1 kHz. With the Start Trigger set to Edge and the Stop Trigger set between 100 samples
to 1000 samples on one device, the trigger signal is off by up to 75 ms scanning one channel on 
each device. This usually (but not always) happens on the scan after changing the sample count used 
for the stop trigger.

----
Help
----

|623684|
Problems can occur using older versions of browsers to view the DAQami help.

You may encounter problems viewing embedded videos, graphics, and other DAQami
help content when using an older browser such an Internet Explorer 8, which 
is native to Windows 7. 

Workaround: Measurement Computing recommends installing the latest version of your browser
for best results viewing the help.

|479449|
Unable to view active content (embedded videos) in DAQami help
using Internet Explorer. 

Workaround: Change the IE security settings to allow active content
to run (Options > Advanced tab) then Restart Internet Explorer.


=============================
7. Fixed Issues
=============================

Version 4.2.0

|636424| Cannot open a configuration file saved with both a USB-CTR Series and
a USB-2416 Series device.

Configurations files saved with a USB-CTR Series and a USB-2416 Series device can now 
be opened in DAQami.


Version 4.0.0

|381519| Overlapping cursor values can be read by zooming in on the display.

|387230| Slow performance is common immediately after a host PC returns
from hibernate/sleep mode. Refer to your PC documentation and support
resources to learn how to minimize this behavior.

|401042| Data on a Strip display now scrolls as cursors are moved left or right
off the edge of the chart. Cursors can no longer be moved beyond the left or right
edge of the chart on a Block display.

|458346| A DAQami installation/repair does not proceed until DAQami closes.
If DAQami is running during an uninstall, it will be completely uninstalled
after the next reboot.

|473375| USB-2408 Series and USB-2416 Series devices can now be configured for
single-ended or differential mode in DAQami.

|484230| With support for multiple devices added to DAQami 4.0.0, adding a device
no longer automatically creates a new configuration, so there is no longer a need
to save a configuration in this scenario.

|519476| The USB-1608HS now supports single-ended acquisitions using DAQami. 

|520375| MCC devices now start a new acquisition after a system crash and reboot.


Version 3.0.1

|584557| DAQami closes without issue when save and close commands are 
executed with the .NET Framework 4.6.1 installed.


Version 3.0

|484227| The X-axis properly aligns with data during a live acquisition.

|468991| All displays are synchronized with the elapsed timer.

|488124| Support added for Bluetooth communication.


Version 2.1

|458102| A message displays when attempting to open a configuration file
that has been moved or deleted.

|463679| Clicking Refresh properly updates the Hardware list.

|473795| Support added for software-paced scans.

|487854| Support added to copy channel using the <Ctrl> key.

|521786| Manual and Remote network settings can be changed from
the Device tab.




Document Revision 5.0
