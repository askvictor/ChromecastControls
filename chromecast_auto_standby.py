#!/usr/bin/env python3

import pychromecast
import threading
import cec
import time
import argparse

parser = argparse.ArgumentParser(description='Auto-switches off TV/Hifi equipment (via CEC) if a particular Chromecast is inactive/idle.')
parser.add_argument('--setup', action='store_true', help='Initial Setup')
parser.add_argument('--chromecast', default='Living Room TV', help='Name of Chromecast to monitor (default: "Living Room TV"')
parser.add_argument('--cec', type=int, default=5, help='Number of CEC device to monitor (default: 5)')
parser.add_argument('--volume', dest='volume', action='store_true', help='Send CEC Volume commands when Chromecast changes volume')
parser.set_defaults(volume=False)
parser.add_argument('--timeout', type=int, default=300, help='Time (seconds) between Chromecast going idle and device power down (default: 300 (=5min))')

args = parser.parse_args()

if args.setup:
    print("Getting CEC Devices")
    cec.init()
    cec_devs = []
    all_devs = cec.list_devices()
    [ print(i, all_devs[i].osd_string) for i in all_devs ]
    cec_dev = input("Select a CEC Device to power down (don't select Chromecast here): ")
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
    chromecast = input("Select a Chromecast device to monitor for idle: ")
    while True:
        try:
            if int(chromecast) < len(chromecasts) and int(chromecast) >= 0:
                break
        except ValueError:
            pass
        chromecast = input("Type the number of a listed device: ")
    cc = chromecasts[int(chromecast)].device.friendly_name
    print(f'Options: --cec {cec_devs[0]} --chromecast "{cc}"')
    exit()

CHROMECAST_NAME = args.chromecast
TIMEOUT = args.timeout
CEC_DEV_ADDRS = [args.cec]
 
# send CEC volume changes when Chromecast's volume has changed
# this fixes the annoyance that CC won't change volume for media
# with surround sound. Doesn't work once CC's internal volume counter
# has reached its maximum
MIRROR_VOLUME = args.volume


class StatusListener:
    def __init__(self, cast, cec_devs, timeout=300):
        self.cast = cast
        self.timeout = timeout
        self.create_timer()
        self.cec_devs = cec_devs

    def new_cast_status(self, status):
        if MIRROR_VOLUME:
            if status.volume_level > self.volume_level:  #volume up
                print("vol up")
                cec.volume_up()
            elif status.volume_level < self.volume_level:  #volume down
                print("vol down")
                cec.volume_down()
            self.volume_level = status.volume_level

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
cec.init()
all_devs = cec.list_devices()

cec_devs = []
for cec_dev_addr in CEC_DEV_ADDRS:
    cec_devs.append(all_devs[cec_dev_addr])

# set up Chromecast
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
    #input('Listening for Chromecast events...\n\n')
