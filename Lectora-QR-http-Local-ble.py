#!/usr/bin/python
# /etc/init.d/noip
# import the necessary packages
import logging
import datetime as dt
import imutils
import argparse
import time
import os
import csv
import urllib3
import RPi.GPIO as GPIO
import configparser
import io
import boto3
from gpiozero import LED
import requests
import json
from uuid import getnode as get_mac
from PIL import Image
import eventlet
import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic
from example_gatt_server import register_app_cb, register_app_error_cb

f = open("PID.txt", "w")
f.write(str(os.getpid()))
f.close()
   
######serial number of the device
cpuserial = "0000000000000000"
try:
 f = open('/proc/cpuinfo','r')
 for line in f:
  if line[0:6]=='Serial':
   cpuserial = line[10:26]
 f.close()
except:
 cpuserial = "ERROR00000000000"
print(cpuserial)

######  Opens conf file
with open("/home/pi/Documents/QRscan/Lectora-QR.ini") as fini:
   garitappiot_config = fini.read()
   configLec = configparser.RawConfigParser()
   #configLec.readfp(io.BytesIO(garitappiot_config))
   configLec.read('/home/pi/Documents/QRscan/Lectora-QR.ini')

######Get ID residential and name
iptipo = configLec.get('garitappiot','tipo')
ipfuncion = configLec.get('garitappiot','funcion')
iptipoIoT = configLec.get('garitappiot','tipoIoT')
   
######logging details
d = dt.datetime.now()
date = str(d.strftime("%d"))+"-"+str(d.strftime("%m"))+"-"+str(d.year)+"_"+cpuserial
logging.basicConfig(filename='/home/pi/Documents/QRscan/logs_'+cpuserial+'/lectora_'+ date +'.log', filemode='a',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

###PID in logging
logging.info(os.getpid())

#####MAC ADDRESS
mac = get_mac()
print(mac)

#######GPIO to use the sensor, led, pluma
distance = 26
led = LED(16)
pluma = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(distance, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

c = "\'"+ cpuserial +"\'"
m = "\'"+ str(mac) +"\'"

# api-endpoint 
URLB = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/boot"
  
# defining a params dict for the parameters to be sent to the API 
PARAMS = {'cpu_serial':c,'type':iptipoIoT,'mac':m} 
print(PARAMS)  
# sending get request and saving the response as response object 
while True:
    try:
        r = requests.get(url = URLB, params = PARAMS)
        #r = http.request('GET', url = URLB, params = PARAMS)
        break
    except:
        logging.info('Error descargando configuracion inicial')
    pass
        
# extracting data in json format 
message = r.json()
print(message)
a = message['message']

if ipfuncion == 'Entrada' and iptipo == 'CONRF':
    #a = bootInfo.credentials
    IP = a.split(",")[0]
    idR = a.split(",")[1]
    nameR = a.split(",")[2]
    URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/entradas"
    print (IP)
    print (idR)
    print (nameR)
if ipfuncion == 'Salida' and iptipo == 'CONRF':
    #a = bootInfo.credentials
    IP = a.split(",")[0]
    idR = a.split(",")[1]
    nameR = a.split(",")[2]
    URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/salidas"
    print (IP)
    print (idR)
    print (nameR)
if ipfuncion == 'Entrada' and iptipo != 'CONRF':
    #a = bootInfo.credentials
    idR = a.split(",")[0]
    nameR = a.split(",")[1]
    URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/entradas"
    print(idR)
    print(nameR)
if ipfuncion == 'Salida' and iptipo != 'CONRF':
    #a = bootInfo.credentials
    idR = a.split(",")[0]
    nameR = a.split(",")[1]
    URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/salidas"
    print(idR)
    print(nameR)

URLV = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/Actualizacion-invitacion-lectora"
global master1
master1 = []
URLM = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/code-master-lectora-http"
#Download master
PARAMSM = {'cpu_serial':c,'idR':idR} 
print(PARAMSM)  
# sending get request and saving the response as response object 
while True:
    try:
        master0 = requests.get(url = URLM, params = PARAMSM)
        break
    except:
        pass
    pass
master1 = master0.json()
print(master1)

def localcall(barcodeData, idR, c, URL, URLV, date, csv):
    ######Datetime
    registry = dt.datetime.now()
    
    value = 0
    for x in master1:
        if barcodeData == x:
            value = 1
            pass
        else:
            pass
        pass
    if value == 1:
        GPIO.setup(pluma, GPIO.OUT)
        GPIO.output(pluma, GPIO.LOW)
        time.sleep(1)
        GPIO.output(pluma, GPIO.HIGH)
        GPIO.setup(pluma, GPIO.IN)
        logging.info ('Acceso concedido')
        csv.write("{},{},{}\n".format(registry,barcodeData,"Valido"))
        csv.flush()
        time.sleep(3)
        pass
    else:
        print("No Encontrado")
        awsCall(barcodeData, idR, c, URL, URLV)
        pass
    return

def awsCall(barcodeData, idR, c, URL, URLV):
    #Send AWS
    z = datetime.strftime("%A")
    arrival_time = str(time.strftime("%H:%M"))
    Day = z.lower()
    qr = str(barcode)

    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'qrCode':barcodeData,'arrival_time':arrival_time,'Day':Day,'residential_id':idR,'cpu_serial':c} 
    print(PARAMS)  
    # sending get request and saving the response as response object
    conexion = False
    try:
        with eventlet.Timeout(10):
            r = requests.get(url = URL, params = PARAMS)
    except:
        logging.info ('Error al verificar el codigo')
        time.sleep(4)
        return

    # extracting data in json format 
    try:
        message = r.json()
        print(message)
        QRstatus = message['result']
        logging.info ('%s', QRstatus)
    
        tipolector = configLec.get('garitappiot','tipo')
        funcionlector = configLec.get('garitappiot','funcion')

        if funcionlector == 'Entrada' and tipolector == 'CONRF':
              if QRstatus == "Valido": fotofile = message['photo']
              if QRstatus == "Invalido": fotofile = "no valido"
              fotofile = message['photo']
              cortesia = "Bienvenido"
              print(QRstatus,fotofile)
        if funcionlector == 'Salida' and tipolector == 'CONRF':
              if QRstatus == "Valido": fotofile = message['photo']
              if QRstatus == "Invalido": fotofile = "no valido"
              cortesia = "Buen viaje"
              print(QRstatus,fotofile)
        if funcionlector == 'Entrada' and tipolector =='NORF':
              fotofile = "norfacial"
              cortesia = "Bienvenido"
        if funcionlector == 'Salida' and tipolector == 'NORF':
              fotofile = "norfacial"
              cortesia = "Buen viaje"

        print(QRstatus, cortesia, fotofile)
        if QRstatus == "Invalido":
            led.on()
            time.sleep(2)
            led.off()
            time.sleep(3)
        if QRstatus == "Valido" and tipolector == 'CONRF':
            for x in range(3):
                logging.info ('Comenzando reconocimiento facial')
                os.system('sudo wget http://'+ IP +':9000/?action=snapshot -O /home/pi/Documents/QRscan/cara.jpg')
                img = Image.open("/home/pi/Documents/QRscan/cara.jpg")
                img.save("/home/pi/Documents/QRscan/patron.jpg", dpi=(640,480))
                targetFile = '/home/pi/Documents/QRscan/patron.jpg'
                sourceFile = fotofile
                coincidence = 0
                client=boto3.client('rekognition')
                imageTarget=open(targetFile,'rb')
                try:
                    response=client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':'garitapp.guest.id.pictures','Name':sourceFile}},
                                  TargetImage={'Bytes': imageTarget.read()})
                    for faceMatch in response['FaceMatches']:
                        similarity = str(faceMatch['Similarity'])
                        coincidence = float(similarity)
                    print(coincidence)
                    logging.info ('Similitud de un %s', similarity)
                    imageTarget.close()
                    if coincidence >= 85:
                        GPIO.setup(pluma, GPIO.OUT)
                        GPIO.output(pluma, GPIO.LOW)
                        time.sleep(1)
                        GPIO.output(pluma, GPIO.HIGH)
                        GPIO.setup(pluma, GPIO.IN)
                        logging.info ('Acceso concedido')
                        csv.write("{},{},{},{}\n".format(datetime,barcodeData,"Valido",coincidence))
                        csv.flush()
                        #validate if it is simple invitation
                        if barcodeData.split("_")[0] == "001":
                            # defining a params dict for the parameters to be sent to the API 
                            PARAMS = {'qrCode':barcodeData,'arrival_time':arrival_time,'Day':Day,'residential_id':idR,'cpu_serial':c}   
                            # sending get request and saving the response as response object
                            while True:
                                try:
                                    with eventlet.Timeout(10):
                                        r = requests.get(url = URLV, params = PARAMS)
                                    break
                                except:
                                    pass
                    else:
                        logging.info ('Acceso denegado')
                        csv.write("{},{},{}\n".format(datetime,barcodeData,"Invalido"))
                        csv.flush()
                        time.sleep(3)
                    break
                except:
                    logging.info ('Usuario no detectado')
                    csv.write("{},{},{}\n".format(datetime,barcodeData,"Invalido"))
                    csv.flush()
                    time.sleep(5)
        if QRstatus == "Valido" and tipolector == 'NORF':
            GPIO.setup(pluma, GPIO.OUT)
            GPIO.output(pluma, GPIO.LOW)
            time.sleep(1)
            GPIO.output(pluma, GPIO.HIGH)
            GPIO.setup(pluma, GPIO.IN)
            logging.info ('Acceso concedido')
            csv.write("{},{},{}\n".format(datetime,barcodeData,"Valido"))
            csv.flush()
    except:
        logging.info ('Error leyedo datos')
        time.sleep(5)
    pass

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="/home/pi/Documents/QRscan/logs_"+cpuserial+"/barcodes_"+cpuserial+"_"+date+".csv",
    help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())
# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "a")
found = set()

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =                    mac
mainloop = None
 
class TxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)
 
    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True
 
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
 
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
 
class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)
 
    def WriteValue(self, value, options):
        print('remote: {}'.format(bytearray(value).decode()))
        logging.info('Codigo leido: %s', format(bytearray(value).decode()))
        localcall(format(bytearray(value).decode()), idR, cpuserial, URL, URLV, date, csv)
 
class UartService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))
 
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
 
    def get_path(self):
        return dbus.ObjectPath(self.path)
 
    def add_service(self, service):
        self.services.append(service)
 
    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response
 
class UartApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))
 
class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True
 
def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
            return o
        print('Skip adapter:', o)
    return None
 
def main():
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    if not adapter:
        print('BLE adapter not found')
        return
 
    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)
 
    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)
 
    mainloop = GLib.MainLoop()
 
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)
    try:
        mainloop.run()
    except KeyboardInterrupt:
        adv.Release()
 
if __name__ == '__main__':
    main()