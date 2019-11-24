#!/usr/bin/env python3

import pychromecast
import threading
import cec
import time

# Configurable options
TIMEOUT = 300  # timeout in seconds
CEC_DEV_ADDRS = [5]  # the device addresses of the devices you want to power off
                     # if only one device, it still needs to be in brackets (a list)
CHROMECAST_NAME = "Living Room TV"  # the name of the Chromecast to monitor

#TODO - split config into seperate file

class StatusListener:
    def __init__(self, cast, cec_devs, timeout=300):
        self.cast = cast
        self.timeout = timeout
        self.create_timer()
        self.cec_devs = cec_devs

    def new_cast_status(self, status):
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

