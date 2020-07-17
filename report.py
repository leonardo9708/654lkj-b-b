import requests

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

# api-endpoint 
URLR = "https://2atle79tca.execute-api.us-east-1.amazonaws.com/dev/iot/send-iot-report-lectora"
  
# defining a params dict for the parameters to be sent to the API 
PARAMS = {'cpu_serial':cpuserial,'state':"1"} 
# sending get request and saving the response as response object 
try:
    r = requests.get(url = URLR, params = PARAMS)
    #r = http.request('GET', url = URLB, params = PARAMS)
except:
    print("Conexion no valida")
pass
