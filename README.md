Please use a linux distro for the following, Mac will also work but just be aware of different port names

To effectively use Micropython on the M5stack you will need python3, esptool.py, and adafruit-ampy 
```zsh
pip3 install esptool
pip3 install adafruit-ampy
```


# First you will need flash Micropython onto your M5Stack Gray
Connect the M5stack to you computer and verify that it is connected by checking /dev
```zsh
ls /dev |grep ttyUSB
```
You should see it on ttyUSB0, if there are multiple ttyUSB* then remove peripherals connected to your computer or take note of the tty that the m5stack uses and replace accordingly within upload.sh.

```zsh
cd firmware
sh upload.sh
```
This should install a special version of micropython able to utilize the M5stacks on board peripherals.
to test this connect to the board via serial. (once again replace ttyUSB0 with your port if needed)

```zsh
screen /dev/ttyUSB0 115200 
```
you should get a REPL and you can issue a few commands

```zsh
from machine import lcd
lcd.print("hello!")
```
To terminate the screen press (crtl+shift+a then the \ key and finally y)

# Getting umqtt
```zsh
cd install_umqtt
``` 

next create a hotspot or find a 2.4ghz router with a good internet connection, note the ssid and password.
You will be downloading a python library directly to the M5stack using upip (u - means micro)

edit main.py (in the install_umqtt directory) to use your ssid and password. Then place it on the device.

```zsh
ampy -p /dev/ttyUSB0 -b 115200 put main.py
```
This will attempt to write whatever is in main.py in your cwd to the device via serial, if it doesn't work the first time, connect to the m5stack via serial (i.e. screen) and make sure you can get a REPL. If not, hard reset the device with the reset button and spam ctrl+c to stop whatever main.py is blocking your device. Once you get the prompt, ">>>", you can terminate the screen and use ampy.

Once this main.py is on your device and connected to your ap (which you provided the ssid and password for), connect to it via serial and issue the following commands

```zsh
import upip
upip.install('micropython-umqtt.simple')
```
Now you should have umqtt.simple install on your device, it persists event after hard rebooting.

# Solace PubSub
create a solace pubsub account and get the connection information.

you will need, client id, tcp connection string, port and password.

once you have the above, substitute the values in main.py (in the main directory), along with your ssid and password.
once everything has been added move the file over with ampy

```zsh
ampy -p /dev/ttyUSB0 -b 115200 put main.py
```

hard reboot and then enter the try-me tab on the solace cloud. Subscribe to the "device/*" topic and you should see data coming from your device.


