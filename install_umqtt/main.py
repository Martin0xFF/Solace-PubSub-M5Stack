from m5stack import *
from network import WLAN
import upip

ssid = "YOUR SSID"
password = "YOUR PASSWORD"

wlan = WLAN()
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    None

lcd.print("Connect Via serial,\nimport upip and issue\n\'upip.install(\"micropython-umqtt.simple\")\'", 0, lcd.CENTER)
