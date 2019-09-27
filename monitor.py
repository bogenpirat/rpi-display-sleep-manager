#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import datetime as dt
import subprocess

# We're using the board mode, so we'll use PIN numbers instead of the GPIO BCM ones
GPIO.setmode(GPIO.BOARD)

# mine's on pin 7, edit this at your leisure
GPIO_PIR = 7
# duration in seconds for which the screen will remain active after no more movement is detected.
# some sensors might have a delay before they indicate inactivity, so in reality for me this is ~35s.
ON_DURATION = 30

#  set GPIO as input
GPIO.setup(GPIO_PIR,GPIO.IN)

current_state  = 1
read_state = 0
last_high = 0
# logging. set this to /dev/null if you don't care
f = open('/tmp/monitor_activity.log', 'a+')

# comment this to disable the x server's power management because we're gonna take over
subprocess.Popen('xset -dpms', shell=True)

try:
 # wait for the sensor to show up
 while GPIO.input(GPIO_PIR)==1:
   read_state = 0

 print("%s initilized PIR" % dt.datetime.now())

 onTime = dt.datetime.now()

 while True :
   # read the sensor's status
   read_state = GPIO.input(GPIO_PIR)
   print("%s: %d" % (dt.datetime.now(), read_state))

   if read_state == 1:
     last_high = time.time()

   # turn on power
   if current_state == 0 and read_state == 1:
     print("%s Monitor on" % dt.datetime.now())
     subprocess.Popen('/usr/bin/vcgencmd display_power 1', shell=True)
     current_state = 1
     f.write('----------------------\n')
     onTime = dt.datetime.now()
     f.write('%s ON\n' % dt.datetime.now().isoformat())

   # turn off power
   elif current_state == 1 and read_state == 0 and (time.time() - last_high) > ON_DURATION:
     print("%s Monitor off" % dt.datetime.now())
     subprocess.Popen('/usr/bin/vcgencmd display_power 0', shell=True)
     current_state = 0
     f.write('%s OFF\n' % dt.datetime.now().isoformat())
     print((dt.datetime.now() - onTime))
     f.write('%s s spent active\n' % (dt.datetime.now() - onTime).total_seconds())
     f.write('----------------------\n')

   # wait a sec between checks
   time.sleep(1)

except KeyboardInterrupt:
 print(" Exit")
 f.close()
 GPIO.cleanup()
