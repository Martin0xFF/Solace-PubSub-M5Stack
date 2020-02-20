# Preluminary
Please use a linux distro for the following tutorial
* You can dual boot your computer : https://itsfoss.com/install-ubuntu-1404-dual-boot-mode-windows-8-81-uefi/
* You can set up a VM with a linux distro : https://brb.nci.nih.gov/seqtools/installUbuntu.html

To effectively use Micropython on the M5stack you will need python3, esptool.py, and adafruit-ampy 
```zsh
pip3 install esptool
pip3 install adafruit-ampy
```

You will also need an M5Stack gray, this can be found on [Amazon][1] or [the M5Stack Site][2]

[1]:https://www.amazon.ca/M5Stack-Mpu9250-Development-Extensible-Arduino/dp/B07PFVGG2Y/ref=sr_1_1?keywords=m5stack&qid=1582161563&sr=8-1

[2]:https://m5stack.com/products/grey-development-core

## Flash Micropython onto your M5Stack Gray
This repo has a version of micropython for the M5Stack already availible. You can create your own firmware if you clone the following repo: https://github.com/m5stack/M5Stack_MicroPython

1. Connect the M5stack to you computer and verify that it is connected by checking /dev
```zsh
ls /dev |grep ttyUSB
```
**You should see it on ttyUSB0, if there are multiple ttyUSB\* then remove peripherals connected to your computer or take note of the tty that the m5stack uses and replace accordingly within upload.sh.**

2. Enter the firmware directory and call the flash script
```zsh
cd firmware
sh upload.sh
```

This should install a special version of micropython able to utilize the M5Stack's on board peripherals.

3. To test this connect to the board via serial. (once again replace ttyUSB0 with your port if needed)

```zsh
screen /dev/ttyUSB0 115200 
```
you should get a REPL and you can issue a few commands

```zsh
from machine import lcd
lcd.print("hello!")
```
To terminate the screen press (crtl+shift+a then the \ key and finally y)

## Getting umqtt

1. Enter the install_umqtt directory

```zsh
cd install_umqtt
``` 

2. Create a hotspot or find a 2.4ghz router with a good internet connection, note the ssid and password.
You will be downloading a python library directly to the M5stack using upip (u - means micro)

3. edit main.py (in the install_umqtt directory) to use your ssid and password. Then place it on the device.

```zsh
ampy -p /dev/ttyUSB0 -b 115200 put main.py
```
This will attempt to write whatever is in main.py in your cwd to the device via serial, if it doesn't work the first time, connect to the m5stack via serial (i.e. screen) and make sure you can get a REPL. If not, hard reset the device with the reset button and spam ctrl+c to stop whatever main.py is blocking your device. Once you get the prompt, ">>>", you can terminate the screen and use ampy.

4. Once this main.py is on your device and connected to your ap (which you provided the ssid and password for), connect to it via serial and issue the following commands

```zsh
import upip
upip.install('micropython-umqtt.simple')
```
Now you should have umqtt.simple install on your device, it **persists event after hard rebooting.**

**There may be cases when a bad upip installation damages the micropython firmware, in this case, repeat the procedure to flash the firmware**

## Solace PubSub
1. Create a solace pubsub account and get the connection information.
![alt text](https://github.com/Martin0xFF/Solace-PubSub-M5Stack/blob/master/images/connection_details.png)
you will need, client id (username), tcp connection string (MQTT Host), port (after ':' on MQTT Host) and password.

2. Substitute the values from the previous step into main.py (in the main directory), along with your ssid and password.

3. Once everything has been added move the file over with ampy

```zsh
ampy -p /dev/ttyUSB0 -b 115200 put main.py
```

4. Hard reboot and then enter the try-me tab on the solace cloud. Subscribe to the "device/*" topic and you should see data coming from your device.

5. A small physics fact: all objects on the earths surface are accelerating towards it core at ~9.81 m/(s^2). Given this, you can determine which face of the M5Stack corresponds with the x, y, and z accelerometer readings.
