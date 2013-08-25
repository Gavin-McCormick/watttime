Radio Thermostat controller
===========================

Instructions for use of the Radio Thermostat WattTime-controller. This software has been tested with the [Filtrete 3M-50](http://www.radiothermostat.com/filtrete/products/3M-50/), but should work on any wifi-enabled Radio Thermostat device.

You will require a wireless network to use the software.

The software reads a live stream of data from the [WattTime website](http://watttime.com) with information on the cleanliness of the electricity currently being supplied, and uses this to adjust the temperature settings of the thermostat according to user settings.

The user can specify a schedule of when he/she would like the thermostat to operate, and a range of temperatures which are permissible at each time. For example, the user could specify that the thermostat is off from 9am-5pm each day, and then from 5pm-10pm each day the AC should maintain a temperature of 70F 50% of the time, 73F 40% of the time, and 80F 10% of the time. Then the controller will choose between 70F, 73F, and 80F according to the status of the electric grid at any given time.

Supported regions
-----------------
By default, the controller checks every 5 minutes for the current status of the electric grid in your location using the WattTime website. Currently the website supports three regions of the country:

* New England (status updates every 10 minutes)
* California (status updates every hour)
* Pacific Northwest (status updates every hour)

The controller will support additional regions as they are added to the WattTime website.

Installation of the Filtrete 3M-50
----------------------------------

* [Instructions](http://www.radiothermostat.com/filtrete/guides/3M-50-Installation-27may10.pdf) for installing the 3M-50 device.
* The 3M-50 requires a 24V external power source (not the batteries) to power the wifi module. This is provided by the "C wire" of your HVAC system. If your HVAC system does not have a "C wire", you will need to purchase a 24V transformer to power the thermostat. Video instructions for attaching the transformer are [here](http://www.youtube.com/watch?v=8a_f2_iAW1U&feature=c4-overview-vl&list=PLE1A61036145003E7).
* Once you have an external 24V power supply, insert the wifi module into either of the two slots in the back of the thermostat. (This should be done when the device is off.)
* [Instructions](http://www.radiothermostat.com/filtrete/guides/SettingupWifiPC.pdf) for connecting the thermostat to the wireless network.
* If you have problems with your setup, you can find further videos and guides [here](http://www.radiothermostat.com/filtrete/help/).

Installation of the WattTime controller
---------------------------------------

* Install [Python](http://www.python.org/download/). The software has been written and tested with Python 3.2 but should also function on Python 2.7. (Python 3.3 is very similar to Python 3.2 and the software should work with Python 3.3 as well, but has not been tested yet.)
* Download the files `config.py`, `datastream.py`, `run.py`, `settings.py`, and `thermostat.py` from this directory. Place these files in a dedicated directory.
* Edit the file `config.py` according to the desired preferences.

Running the WattTime controller
-------------------------------

* Open a terminal and go to the folder where you have downloaded the controller.
* Run `python run.py`.
* When you wish to stop the software (for example if you want to manually control the temperature), press Ctrl-C.
