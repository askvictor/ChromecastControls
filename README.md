# ChromecastControls
Implements better CEC controls for Chromecasts. Currently has two functions:
* checks if a particular Chromecast is idle, and switches off specified TV/Hifi equipment after a timeout. Will save energy being wasted by having your TV or hifi on when you're not watching anything.
* sends CEC volume commands when Chromecast volume is changed (useful for surround-sound media which Chromecast doesn't let you control volume for)

Tested on Raspberry Pi running Raspbian Buster. 
## Installation (without VirtualEnv)
1. Set up Raspbian (Buster) on your Raspberry Pi. Make sure it's connected to the same network (either Ethernet or Wifi) as your Chromecast. The HDMI port also needs to be connected to the TV or receiver your Chromecast is connected to.
1. Ensure Python 3.7 or later is installed (this is the default in Raspbian Buster)
2. Clone this repository, or [download the zip](https://github.com/askvictor/ChromecastControls/archive/master.zip) and extract the files, then go into the directory thus created.
3. Install CEC in the OS: `sudo apt-get install libcec-dev libcec4`
4. Install requirements: `sudo pip3 install -r requirements.txt`
5. Run `sudo python3 chromecast_controls.py --setup` for interactive setup and install

## Why?
### Power
Chromecast can switch on modern TVs/receivers (using [HDMI CEC](https://en.wikipedia.org/wiki/Consumer_Electronics_Control)) when you start casting to it. But for some reason, Google didn't implement a feature to switch off devices when it's been sitting idle for a while. This wastes power (somewhere in the ballpark of 50-100W). ChromecastControls fixes this by detecting when the Chromecast is sitting idle, and putting any connected equipment into standby.
### Volume
Ever see the message "Surround Sound enabled. To adjust volume, use your TV's remote control" when trying to change the volume for something you're casting from your phone? Chromecast can modify volume for stereo sources, but not surround sound. However, CEC can send a signal to your TV/receiver to change the volume. Why the Chromecast doesn't send this signal is anyone's guess. But ChromecastControls can detect when you've attempted to change the volume via your phone, and sends the corresponding CEC signals to your equipment.

## How?
The [PyChromecast](https://github.com/balloob/pychromecast) library can listen on your network for any events related to your Chromecast. In this case, the events we're listening for are status changes (an app connects to or disconnects from the Chromecast) or volume changes. When ChromecastControls detects such a change it sends a corresponding signal on the HDMI CEC bus to control the equipment (using libcec and [python-cec](https://github.com/trainman419/python-cec). The Raspberry Pi is perfect for this as it has an inbuilt CEC signalling in the HDMI connector - most computers don't have this (you could try a Pulse-8 adapter, but this hasn't been tested). For standby/power-off, ChromecastControls first waits for a set amount of time before turning things off.
