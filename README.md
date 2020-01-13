# ChromecastControls
Implements better CEC controls for Chromecasts. Currently has two functions:
* checks if a particular Chromecast is idle, and switches off specified TV/Hifi equipment after a timeout. Will save energy being wasted by having your TV or hifi on when you're not watching anything.
* sends CEC volume commands when Chromecast volume is changed (useful for surround-sound media which Chromecast doesn't let you control volume for)

Tested on Raspberry Pi running Raspbian. 
## Installation (without VirtualEnv)
1. Ensure Python 3.7 or later is installed (this is the default in Raspbian Buster)
2. Clone this repository, or [download the zip](https://github.com/askvictor/ChromecastControls/archive/master.zip) and extract the files, then go into the directory thus created.
3. Install CEC in the OS: `sudo apt-get install libcec-dev libcec4`
4. Install requirements: `sudo pip3 install -r requirements.txt`
5. Run `sudo python3 chromecast_controls.py --setup` for interactive setup and install

## Installation (VirtualEnv) - TODO - write instructions
