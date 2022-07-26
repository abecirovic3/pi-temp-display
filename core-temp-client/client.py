import subprocess
import re
import requests
import json
import time
import argparse

parser = argparse.ArgumentParser(description='Program to read CPU core temps and send data to local server')
parser.add_argument('-d', '-D', default=10, type=int, help='Frequency of reading the CPU temp and sending a request to server, in seconds', dest='delay')
parser.add_argument('url', help='The URL of the local server. For instance: http://192.168.1.10:5000/temp')
args = vars(parser.parse_args())

command = 'sensors'
API_ENDPOINT = args['url']
delay = args['delay']
headers = {'Content-Type': 'application/json'}

while True:
  print('Reading temp...')
  temp = subprocess.Popen([command], stdout = subprocess.PIPE)

  output = str(temp.communicate())

  lines = output.split("\\n")

  obj = {}

  for line in lines:
    if line.startswith("Core"):
      line = line.replace("\\xc2\\xb0C", "")
      data = re.findall("Core (\d):\s*\+([\d\.]+)\s*\(high = [\+\d\.]+, crit = \+([\d\.]+)", line)
      obj[data[0][0]] = {
        "temp": float(data[0][1]),
        "crit": float(data[0][2])
      }
      
  try:    
    r = requests.post(url = API_ENDPOINT, data = json.dumps(obj, indent = 4), headers = headers)
    print('Response: ', r.text)
  except:
    print('Request failed, check your URL, or your local server')
  
  time.sleep(delay)