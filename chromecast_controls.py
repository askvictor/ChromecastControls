#!/usr/bin/env python3

import pychromecast
import threading
import cec
import time
import argparse
import sys
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(description='Checks if a particular Chromecast is idle, and switches off specified TV/Hifi equipment after a timeout. Also allows controlling of volume by CEC for surround-sound media.')
parser.add_argument('--setup', action='store_true', help='Initial Setup')
parser.add_argument('--chromecast', default='Living Room TV', help='Name of Chromecast to monitor (default: "Living Room TV"')
parser.add_argument('--cec', type=int, default=5, help='Number of CEC device to monitor (default: 5)')
parser.add_argument('--volume', dest='volume', action='store_true', help='Send CEC Volume commands when Chromecast changes volume')
parser.set_defaults(volume=False)
parser.add_argument('--standby', dest='standby', action='store_true', help='Put Hifi into standby when Chromecast is idle')
parser.set_defaults(standby=True)
parser.add_argument('--timeout', type=int, default=300, help='Time (seconds) between Chromecast going idle and device power down (default: 300 (=5min))')

args = parser.parse_args()


if args.setup:
    if os.geteuid() == 0:  # we have root/sudo
        pass
    else:
        print(f"To set up, please run as root:\n sudo ./{sys.argv[0].split('/')[-1]} --setup")

    print("Getting CEC Devices")
    cec.init()
    cec_devs = []
    all_devs = cec.list_devices()
    [ print(i, all_devs[i].osd_string) for i in all_devs ]
    cec_dev = input("Select a CEC Device to control (don't select Chromecast here): ")
    while True:
        try:
            if int(cec_dev) in all_devs:
                break
        except ValueError:
            pass
        cec_dev = input("Type the number of a listed device: ")
    #TODO - allow multi devices
    cec_devs.append(cec_dev)

    print("\nGetting Chromecasts on network")
    chromecasts = pychromecast.get_chromecasts()
    [ print(i, cc.device.friendly_name) for i, cc in enumerate(chromecasts) ]
    chromecast = input("Select a Chromecast device to monitor: ")
    while True:
        try:
            if int(chromecast) < len(chromecasts) and int(chromecast) >= 0:
                break
        except ValueError:
            pass
        chromecast = input("Type the number of a listed device: ")
    cc = chromecasts[int(chromecast)].device.friendly_name

    vol = "z"
    while vol not in "yn":
        vol = input("Would you like to control hifi volume via Chromecast/phone controls? (y/n) ").lower()

    sb = "z"
    while sb not in "yn":
        sb = input("Would you like to put hifi equipment into standby when Chromecast is idle? (y/n) ").lower()

    options = f'--cec {cec_devs[0]} --chromecast "{cc}"{" --volume" if vol == "y" else ""}{" --standby" if sb == "y" else ""}'
    if os.geteuid() == 0:  # we have root/sudo
        print("copying myself into /usr/local/bin")
        shutil.copy2(sys.argv[0], "/usr/local/bin")
        print("creating systemd service")
        template = open("chromecast_controls@USERNAME.service")
        service_name = f'chromecast_controls@{os.getenv("SUDO_USER")}.service'
        servicefile = open( f'/etc/systemd/system/{service_name}',"w")
        for line in template:
            if "ExecStart" in line:
                line = line.rstrip() + " " + options
            servicefile.write(line)
        servicefile.close()
        print("installing into systemd")
        subprocess.run(["systemctl", "daemon-reload"])
        print("starting Chromecast Control service")
        subprocess.run(["systemctl", "start", service_name])
    else:
        print(f'Options for manual setup: {options}')

    exit()
else:
    print(f"To set up, please run:\n sudo ./{sys.argv[0].split('/')[-1]} --setup")

CHROMECAST_NAME = args.chromecast
TIMEOUT = args.timeout
CEC_DEV_ADDRS = [args.cec]

# send CEC volume changes when Chromecast's volume has changed
# this fixes the annoyance that CC won't change volume for media
# with surround sound.
MIRROR_VOLUME = args.volume


class StatusListener:
    def __init__(self, cast, cec_devs, timeout=300):
        self.cast = cast
        self.timeout = timeout
        self.create_timer()
        self.cec_devs = cec_devs
        self.volume_level = None

    def new_cast_status(self, status):
        if MIRROR_VOLUME:
            if self.volume_level is None:
                if status.volume_level == 0:
                    self.volume_level = 0.1
                elif status.volume_level == 1:
                    self.volume_level = 0.9
                else:
                    self.volume_level = status.volume_level
            else:
                print(f"cc: {status.volume_level}, self: {self.volume_level}")
                if status.volume_level > self.volume_level:  #volume up
                    print("vol up")
                    if status.volume_level == 1:
                        self.cast.volume_down()  # to get around max volume problem
                    else:
                        self.volume_level = status.volume_level
                    cec.volume_up()
                elif status.volume_level < self.volume_level:  #volume down
                    print(f"vol down")
                    if status.volume_level == 0:
                        self.cast.volume_up()  # to get around min volume problem
                    else:
                        self.volume_level = status.volume_level
                    cec.volume_down()

        if status.status_text:
            print('app connection: ', status.status_text)
            self.cancel_timer()
        else: # no app connection
            print('no app connection; starting timer')
            self.start_timer()

    def create_timer(self):
        self.timer = threading.Timer(self.timeout, self.timer_expired)

    def start_timer(self):
        if not self.timer.is_alive():
            self.timer.start()

    def cancel_timer(self):
        self.timer.cancel()
        self.create_timer()

    def timer_expired(self):
        print("timer expired")
        for cec_dev in self.cec_devs:
            cec_dev.standby()
        self.create_timer()


# set up CEC
print("setting up CEC")
cec.init()
print("getting CEC devices")
all_devs = cec.list_devices()

cec_devs = []
for cec_dev_addr in CEC_DEV_ADDRS:
    cec_devs.append(all_devs[cec_dev_addr])

# set up Chromecast
print("getting Chromecasts")
chromecasts = pychromecast.get_chromecasts()
chromecast = next(cc for cc in chromecasts
                  if cc.device.friendly_name == CHROMECAST_NAME)
chromecast.start()

# connect statuslistener
listenerCast = StatusListener(chromecast, cec_devs, TIMEOUT)
chromecast.register_status_listener(listenerCast)

# sit back and wait
print('Listening for Chromecast events...\n\n')
while True:
    time.sleep(0.2)

