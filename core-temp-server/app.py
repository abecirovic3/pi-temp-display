from flask import Flask, request

from queue import Queue

import threading
import time

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.virtual import viewport

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=2, rotate=2, block_orientation=90)

app = Flask(__name__)

@app.route('/')
def index():
  return 'Server Works!'

@app.route('/temp', methods=['POST'])
def add_temp():
  if not temps.full():
    temps.put(request.json)
  return 'OK'


temps = Queue(maxsize = 100)
last_temp = {}
crit_temp_factor = 0.85

def print_core_temp():
  global last_temp
  while True:
    if not temps.empty():
      t = temps.get()
      if len(last_temp) == 0:
        last_temp = t
      msg = ''
      for key in t:
        sign = '/'   # sing indicates the temp direction (etc. rising, falling..)
        if t[key]['temp'] >= t[key]['crit'] * crit_temp_factor:
          sign = '!'
        else:
          if t[key]['temp'] > last_temp[key]['temp']:
            sign = '+'
          elif t[key]['temp'] < last_temp[key]['temp']:
            sign = '-'
        msg += 'C' + key + ': ' + str(t[key]['temp']) + ' ' + sign + ' '
      show_message(device, msg, fill="white", scroll_delay=0.1)
      last_temp = t
    else:
      show_message(device, "No data ", fill="white", scroll_delay=0.1)

t = threading.Thread(target=print_core_temp)

t.start()
