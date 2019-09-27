# rpi-display-sleep-manager
This is a script for the Raspberry Pi 3 Model B+ that handles turning the display off an on in conjunction with a motion sensor.

```monitor.py``` was written for Python 3. You may have success running it with Python 2.7 after doing some alterations, but why would you? It's *current-year*.

# hardware
## pi
my setup works with a raspberry pi 3 model b+, but the script worked fine on an older raspberry pi model b as well. for older or newer models of the pi, you may have to resort to different commands for controlling the screen power. a google search is worth a try, it sure helped me.

it's running on raspbian 10 (buster), which is currently the latest iteration of raspbian for the pi, and where some things have changed compared to the older versions, particularly in relation to the window manager.

## motion sensor
for the motion sensor, i use a [PIR (passive infra-red) sensor](https://www.amazon.de/gp/product/B008AESDSY).

there are many different models, but most of them should work similarly. it has a range of around 7m and field of view of around 100°, or around 50° in each direction measured from the center axis of the sensor's half sphere. my smart mirror is hung in a hallway, so that's more than enough.

i've attached its pins in the following way:  
* VCC to pin 2 (5V)
* OUT to pin 7 (GPIO4)
* GND to pin 6 (ground)

if you attach OUT differently, be sure to alter the configuration in `monitor.py`.

[here](https://www.theengineeringprojects.com/wp-content/uploads/2018/07/introduction-to-raspberry-pi-3-b-plus-2.png)'s a handy diagram for the pi 3 model b+'s GPIO pins.

# display sleep manager
`monitor.py` contains an active waiting loop and should be started once. as it makes calls to `/usr/bin/vcgencmd` and needs to read GPIO data directly, you need to run it as root.

## run a python script as root
since the linux kernel prevents scripts containing a shebang (indicating an interpreter) from being run via the setuid bit, and your regular logged-in desktop user doesn't have root access without entering a password (stupid to automate), the next best way of running this monitor is to write a small c file that runs as root via the setuid bit and executes the python script.

that's the purpose of `monitor-helper.c`.

be sure to change the path of the python 3 executable if it's different from the one contained in the file. in addition, ideally you should supply the full path of the monitor.py script. so be sure to edit this file.

then compile with
```bash
$ gcc -o monitor-helper monitor-helper.c
```

set the program's owner to root:
```bash
$ sudo chown root monitor-helper
```

set the setuid bit:
```bash
$ sudo chmod u+s monitor-helper
```

some more reading material to evaluate how great of an idea this is: https://en.wikipedia.org/wiki/Setuid

now, if you've got an X session running, you should be able to start the monitor by running (as a regular old user):
```bash
$ DISPLAY=:0 ./monitor-helper
```

## autostarting the monitoring script
as previously mentioned, raspbian 10 and its default window manager have a new place for launching applications, and most information on how to do it available on the internet right now is a bit dated.

first, edit the LXDE-pi autostart file. you may have to create it, in addition to creating the folders it resides in.
```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```
fill it with these contents:
```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
point-rpi
@xrandr --output HDMI-1 --rotate left
@xset s off
@xset -dpms
@xset s noblank
@/home/julian/bin/monitor-helper
```
as this user config file overrides the system-wide one, we need to launch a bunch of applications to have LXDE run properly.
some notes:
- the xrandr line rotates the display. this may not be necessary for you depending on your screen orientation.
- the xset lines are necessary in order to disable dpms and power saving functionality used by the X server
- the last line should contain the full path to the helper program that runs the monitoring script

# faq
Q: **isn't running a user-editable script as root a really stupid idea?**

A: hell yeah. but the alternative would be to put a bunch of logic into the script that waits for the x server to run, and then put it into root's cron. but that's a) not really very portable and b) i was too lazy to do this.


Q: **i don't have vcgencmd, what now?**

A: vcgencmd wasn't always part of raspbian. it's currently part of the firmware package, and the functionality of turning off the power to the hdmi port could be moved elsewhere in the future. be sure to give google a try, that's how i eventually arrived at most of the information in this document.


Q: **rotating the screen doesn't work or performance is shitty. what's your video driver of choice?**

A: i ended up putting these lines in `/boot/config.txt`:
```
[all]
dtoverlay=vc4-kms-v3d
```
