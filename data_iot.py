import requests
import json
import subprocess
from uuid import getnode as get_mac
import socket
import fcntl
import struct

####Bluetooth mac
cmd = "hciconfig"
device_id = "hci0" 
status, output = subprocess.getstatusoutput(cmd)
bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
print(bt_mac)

####CPU SERIAL
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

#####MAC ADDRESS
mac = get_mac()
print(mac)

'''######IP
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

r = get_ip_address('wlan0') '''
from ipgetter2 import ipgetter1 as ipgetter
IP = ipgetter.myip()
print(IP)
  
# api-endpoint 
URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot_address_report" #produccion
#URL = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/verificar-visita-qr-lectora" #pruebas

# defining a params dict for the parameters to be sent to the API 
PARAMS = {'cpu_serial':str(cpuserial), 'mac':str(mac), 'IP':str(IP), 'bt_mac':bt_mac}
  
# sending get request and saving the response as response object 
r = requests.get(url = URL, params = PARAMS) 


# extracting data in json format 7
message = r.json()
print(message)
result = message['result']

print(result)