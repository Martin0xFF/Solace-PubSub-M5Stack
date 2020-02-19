from m5stack import *
from network import WLAN
from umqtt.simple import MQTTClient
from machine import I2C, Timer

ssid = "YOUR SSID"
password = "YOUR PASSWORD"

# The M5stack gray has an i2c Accelerometer + Gyroscope
# We create an i2c interface with pins 21 and 22
# This version of Micropython is slightly older and hence
# We can input the pin numbers directly

i2 = I2C(freq=400000, sda=21, scl=22)
mpu_address = 0x68


# We create a wlan interface object using default config
# This puts the M5stack in Station mode, connecting to 
# an AP such as a router or your phone

wlan = WLAN()

# Here we enable the antenna, now it is broadcasting

wlan.active(True)

# Connect using ssid and password from before

wlan.connect(ssid, password)

# save the screen dimensions in monitorwidth (mw)
# and monitorheight(mh)

mw, mh = lcd.screensize()

# set the font, you can find the different fonts by 
# connecting via serial and calling help(lcd)

lcd.font(lcd.FONT_Ubuntu)

# data from i2c will be in 2's complement, but python
# does not automatically convert, here we create a function
# to do the conversion for us 

def complement(val):
    if (val & (1 << 15)) !=0: 
        val = val - (1 << 16)
    return val


   
def check_connect():
    lcd.clear()
    if wlan.isconnected():
        lcd.print('Connected!',lcd.CENTER, 2*mh//3+2, 0xffffff, transparent = True)
    else:
        lcd.print('Not Connected', lcd.CENTER, 2*mh//3+2, 0xffffff, transparent = True)

# Collects mpu data and displays on lcd

def accel(timer):
    x_accel = complement(i2.readfrom_mem(mpu_address, 0x3b, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x3c, 1)[0])
    x_accel = x_accel*9.81/16600
    y_accel = complement(i2.readfrom_mem(mpu_address, 0x3d, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x3e, 1)[0])
    y_accel = y_accel*9.81/16600
    z_accel = complement(i2.readfrom_mem(mpu_address, 0x3f, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x40, 1)[0])
    z_accel = z_accel*9.81/16600
    
    # we do a few additional calculations, as requested by the data sheet
    temp =  (complement(i2.readfrom_mem(mpu_address, 0x41, 1)[0] <<8 | i2.readfrom_mem(mpu_address, 0x42, 1)[0]))/326.8 + 25.0 
    
    
    x_gyro = complement(i2.readfrom_mem(mpu_address, 0x43, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x44, 1)[0])
    y_gyro = complement(i2.readfrom_mem(mpu_address, 0x45, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x46, 1)[0])
    z_gyro = complement(i2.readfrom_mem(mpu_address, 0x47, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x48, 1)[0])
    
    # Here we write the data out to the screen for the user to see

    lcd.print('xA: %07.3f yA: %07.3f zA: %07.3f' % (abs(x_accel),abs(y_accel),abs(z_accel)), lcd.CENTER, 184, 0xffffff)
    lcd.print('xG: %07.1f yG: %07.1f zG: %07.1f' % (abs(x_gyro),abs(y_gyro),abs(z_gyro)), lcd.CENTER, 160, 0xffffff)
    lcd.print('temp: %05.2fC' % abs(temp), lcd.CENTER, lcd.BOTTOM, 0xffffff)

# we create a time which will periodically call the accel function every 2 seconds

t1 = Timer(1)
t1.init(period=2000, mode=t1.PERIODIC, callback=accel)


# we create function to send motion data to the cloud periodically

def pub(timer):
    x_accel = complement(i2.readfrom_mem(mpu_address, 0x3b, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x3c, 1)[0])    
    x_accel = x_accel*9.81/16600
   
    y_accel = complement(i2.readfrom_mem(mpu_address, 0x3d, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x3e, 1)[0])    
    y_accel = y_accel*9.81/16600
    
    z_accel = complement(i2.readfrom_mem(mpu_address, 0x3f, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x40, 1)[0])    
    z_accel = z_accel*9.81/16600
   
    client.publish('device/accel','{x: %05.2f, y: %05.2f, z: %05.2f}' % (x_accel, y_accel, z_accel))

    x_gyro = complement(i2.readfrom_mem(mpu_address, 0x43, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x44, 1)[0])
    y_gyro = complement(i2.readfrom_mem(mpu_address, 0x45, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x46, 1)[0])
    z_gyro = complement(i2.readfrom_mem(mpu_address, 0x47, 1)[0] << 8| i2.readfrom_mem(mpu_address, 0x48, 1)[0])
    
    client.publish('device/gyro','{x: %06.1f, y: %06.1f, z: %06.1f}' % (abs(x_gyro),abs(y_gyro),abs(z_gyro)))
    
    temp =  (complement(i2.readfrom_mem(mpu_address, 0x41, 1)[0] <<8 | i2.readfrom_mem(mpu_address, 0x42, 1)[0]))/326.8 + 25.0 
    
    client.publish('device/temp', '{t: %05.2f}' % abs(temp))




# A button call back to stop accel function

def Acb():
    lcd.clear()
    lcd.image(lcd.CENTER, 0, 'pubsub.jpg',scale=1)
    lcd.print("Data Paused", lcd.CENTER, 160)
    t1.pause()

# B button call back to start accel function again

def Bcb():
    lcd.clear()
    lcd.image(lcd.CENTER, 0, 'pubsub.jpg', scale=1)
    t1.resume()

lcd.image(lcd.CENTER, 0, 'pubsub.jpg', scale=1)
buttonB.wasReleased(Bcb)
buttonA.wasReleased(Acb)


# We block until we can establish a connect to ap
# If you want to upload a new main.py to device via serial
# you will need to create a serial connection then kill this script
# with ctrl-c

while not wlan.isconnected():
    None

# this is the server i.e. br5x0spg1s1l0b.messaging.solace.cloud (remove tcp:// from connection string)
server ="YOUR MQTT SERVER" 
password ="YOUR MQTT PASSWORD" 
# client id
client_id = "solace-cloud-client"

# port (originally found on the end of the connection string)
port = 20518

client = MQTTClient(user=client_id, client_id=client_id,  server=server, port=port,  keepalive=4000, password=password)  
client.connect()


def Ccb():
    client.publish("device/cbutton", "cButton has been pressed!")

buttonC.wasReleased(Ccb)

t2 = Timer(2)
t2.init(period=2000, mode=t2.PERIODIC, callback=pub)
