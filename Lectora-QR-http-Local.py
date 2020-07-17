#!/usr/bin/python
# /etc/init.d/noip
# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import logging
import datetime as dt
import imutils
import time
import os
import cv2
import smbus
import I2C_LCD_driver
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

f = open("PID.txt", "w")
f.write(str(os.getpid()))
f.close()

#######Show on LCD screen
mylcd = I2C_LCD_driver.lcd()
str_pad = " " * 16

######  Opens conf file
with open("/home/pi/Documents/QRscan/Lectora-QR.ini") as fini:
   garitappiot_config = fini.read()
   configLec = configparser.RawConfigParser()
   #configLec.readfp(io.BytesIO(garitappiot_config))
   configLec.read('/home/pi/Documents/QRscan/Lectora-QR.ini')
   
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
   
######logging details
d = dt.datetime.now()
date = str(d.strftime("%d"))+"-"+str(d.strftime("%m"))+"-"+str(d.year)+"_"+cpuserial
print(date)
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

########check connection
while True:
    try:
        http = urllib3.PoolManager()
        p = http.request('GET', 'https://www.google.com')
        logging.info('Conectado')
        break
    except:
        logging.info('Error de conexion buscando configuracion')
        mylcd.lcd_display_string("Error de         ", 1)
        mylcd.lcd_display_string("conexion         ", 2)
        time.sleep(5)
        mylcd.lcd_display_string("Reintentando     ", 1)
        mylcd.lcd_display_string("                 ", 2)



######Get ID residential and name
iptipo = configLec.get('garitappiot','tipo')
ipfuncion = configLec.get('garitappiot','funcion')
iptipoIoT = configLec.get('garitappiot','tipoIoT')

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
        mylcd.lcd_display_string(" Error de        ", 1)
        mylcd.lcd_display_string("conexion inicial ", 2)
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

def sensor_activate():
    while True:
        r = False
        for i in range (0, len(my_long_string)):
            lcd_text = my_long_string[i:(i+16)]
            mylcd.lcd_display_string(lcd_text,1)
            time.sleep(0.4)

            mylcd.lcd_display_string(str_pad,1)
            state = GPIO.input(distance)
            if state == False:
                print('Sensor activado')
                r = True
                break
        if r == True:
            break
        pass

def localcall(barcodeData, idR, c, URL, URLV, csv):
    value = 0
    for x in master1:
        if barcodeData == x:
            value = 1
            pass
        else:
            pass
        pass
    if value == 1:
        mylcd.lcd_display_string("Bienvenido      ",1)
        mylcd.lcd_display_string("                ",2)
        GPIO.setup(pluma, GPIO.OUT)
        GPIO.output(pluma, GPIO.LOW)
        time.sleep(1)
        GPIO.output(pluma, GPIO.HIGH)
        GPIO.setup(pluma, GPIO.IN)
        logging.info ('Acceso concedido')
        csv.write("{},{},{}\n".format(datetime,barcodeData,"Valido"))
        csv.flush()
        time.sleep(3)
        pass
    else:
        awsCall(barcodeData, idR, c, URL, URLV, csv)
        pass
    return

def awsCall(barcodeData, idR, c, URL, URLV, csv):
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
        mylcd.lcd_display_string(" Error de        ", 1)
        mylcd.lcd_display_string("conexion         ", 2)
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
        mylcd.lcd_display_string("                ",1)
        mylcd.lcd_display_string("                ",2)
        mylcd.lcd_display_string(nameR, 1)
        if QRstatus == "Invalido":
            mylcd.lcd_display_string("Codigo Invalido ",2)
            led.on()
            time.sleep(2)
            led.off()
            time.sleep(3)
        if QRstatus == "Valido" and tipolector == 'CONRF':
            mylcd.lcd_display_string("Verificando     ",1)
            mylcd.lcd_display_string("Usuario         ",2)
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
                        mylcd.lcd_display_string(cortesia,2)
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
                        mylcd.lcd_display_string("Ususario         ",1)
                        mylcd.lcd_display_string("no valido        ",2)
                        csv.write("{},{},{}\n".format(datetime,barcodeData,"Invalido"))
                        csv.flush()
                        time.sleep(3)
                    break
                except:
                    logging.info ('Usuario no detectado')
                    mylcd.lcd_display_string("Error de        ",1)
                    mylcd.lcd_display_string("reconocimiento  ",2)
                    csv.write("{},{},{}\n".format(datetime,barcodeData,"Invalido"))
                    csv.flush()
                    time.sleep(5)
        if QRstatus == "Valido" and tipolector == 'NORF':
            mylcd.lcd_display_string("                ",2)
            mylcd.lcd_display_string(nameR, 1)
            mylcd.lcd_display_string(cortesia,2)
            GPIO.setup(pluma, GPIO.OUT)
            GPIO.output(pluma, GPIO.LOW)
            time.sleep(1)
            GPIO.output(pluma, GPIO.HIGH)
            GPIO.setup(pluma, GPIO.IN)
            logging.info ('Acceso concedido')
            csv.write("{},{},{}\n".format(datetime,barcodeData,"Valido"))
            csv.flush()
    except:
        mylcd.lcd_display_string("Codigo Invalido ",2)
        logging.info ('Error leyedo datos')
        time.sleep(5)
    pass


#######Show on LCD screen
#mylcd = I2C_LCD_driver.lcd()
#str_pad = " " * 16
my_long_string = nameR
my_long_string = str_pad + my_long_string

#######Reading QR
mylcd.lcd_display_string("Ingresa QR      ",2)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="/home/pi/Documents/QRscan/logs_"+cpuserial+"/barcodes_"+cpuserial+"_"+date+".csv",
    help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())
# initialize the video stream and allow the camera sensor to warm up
logging.info('[INFO] starting video stream...')
vs = VideoStream(src=0)
vs.start()
#vs = VideoStream(usePiCamera=True).start()

time.sleep(2.0)
sensor_activate()

# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "a")
found = set()

# loop over the frames from the video stream
while True:
    for x in range(1):
        ####Get date
        datetime = dt.datetime.now()
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400, inter=cv2.INTER_CUBIC)

        # find the barcodes in the frame and decode each of the barcodes
        try:
            barcodes = pyzbar.decode(frame)
        except:
            logging.info ('Error al leer codigo')

        # loop over the detected barcodes
        for barcode in barcodes:
                mylcd.lcd_display_string("Procesando      ", 1)
                mylcd.lcd_display_string("Invitacion      ", 2)
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)    

                # the barcode data is a bytes object so if we want to draw it        
                # on our output image we need to convert it to a string first
                try:
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type
                    logging.info('Codigo leido: %s', barcodeData)
                except:
                    logging.info('Error decodificando codigo')
                    break


                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # the timestamp + barcode to disk and update the set
                found.add(barcodeData)
                tipolector = configLec.get('garitappiot','tipo')
                funcionlector = configLec.get('garitappiot','funcion')
                
                if funcionlector == 'Entrada' and tipolector == 'CONRF':
                    awsCall(barcodeData, idR, c, URL, URLV, csv)
                if funcionlector == 'Salida' and tipolector == 'CONRF':
                    awsCall(barcodeData, idR, c, URL, URLV, csv)
                if funcionlector == 'Entrada' and tipolector =='NORF':
                    if barcodeData.split("_")[0] == "master":
                        localcall(barcodeData, idR, c, URL, URLV, csv)
                        pass
                    else:
                        awsCall(barcodeData, idR, c, URL, URLV, csv)
                if funcionlector == 'Salida' and tipolector == 'NORF':
                    if barcodeData.split("_")[0] == "master":
                        localcall(barcodeData, idR, c, URL, URLV, csv)
                        pass
                    else:
                        awsCall(barcodeData, idR, c, URL, URLV, csv)
        pass      
            
    ### comun para todos
    mylcd.lcd_display_string("Ingresa QR      ",2)
    sensor_activate()

    # show the output frame
    #cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    pass

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()

