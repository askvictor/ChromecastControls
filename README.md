# ChromeCastAutoStandby
Checks if a particular Chromecast is idle, and switches off specified TV/Hifi equipment after a timeout. Tested on Raspberry Pi running Raspbian. Will save energy being wasted by having your TV or hifi on when you're not watching anything.

## Installation (without VirtualEnv) - TODO - test these instructions!
1. Ensure Python 3.7 or later is installed (this is the default in Raspbian Buster)
2. Clone this repository, or [download the zip](https://github.com/askvictor/ChromeCastAutoStandby/archive/master.zip) and extract the files, then go into the directory thus created.
3. Install requirements: `sudo pip3 install -r requirements.txt`
3. Install CEC in the OS: `sudo apt-get install libcec-dev libcec4`
4. Run `echo scan | cec-client -s -d 1` to show what devices are on the CEC bus. Find the device(s) you wish to power-down with this program, and remember their device numbers
5. Edit chromecast_auto_standby.py to change the config variables at the top of the file - set the number(s) from the previous step in CEC_DEV_ADDRS and the name of the Chromecast you wish to monitor as CHROMECAST_NAME. Optionally change the timeout value as well (this is how long it will wait between the Chromecast going idle until it switches off the device(s).
6. Test that it works as planned (it's useful to change the timeout value to something small like 10 for testing). Run `python3 chromecast_auto_standby.py` and connect and disconnect apps to the Chromecast to see if it works as desired. Ctrl-C to get out.
7. Copy the main file to /usr/local/bin: `sudo cp chromecast_auto_standby /usr/local/bin`. If you want to keep it somewhere else, that's fine but update the service file with the new location
7. Choose a user to run as (pi is a good idea and will be used for the rest of this example, or you could create a dedicated user for this). Copy the systemd service file to /etc/systemd/system to allow automatic starting at boot time, replacing USERNAME with the user you want to run as: `sudo cp chromecast_auto_standby@USERNAME.service /etc/systemd/system/chromecast_auto_standby@pi.service` 
8. Start the system service `sudo service cc_standby@pi start`

## Installation (VirtualEnv) - TODO - write instructions
