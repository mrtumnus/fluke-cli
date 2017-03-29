#!/usr/bin/python
"""Fluke - Fluke multimeter communication tool

Usage:
  fluke [options] --port=PORT
  fluke --help
  fluke --version

Options:
  -p PORT --port=PORT           Device port name (e.g., COM1, COM11)
  -s FACTOR --scale=FACTOR      Scale factor for measurement
  -r DIGITS --round=DIGITS      # of decimal digits to round to (can be negative)
  -h --help                     Show this screen
  -v --version                  Show version

"""

from __future__ import print_function
import serial
import sys
import re
from docopt import docopt

def readline(port):
	eol = b'\r'
	leneol = len(eol)
	line = bytearray()
	while True:
		c = port.read(1)
		if c:
			line += c
			if line[-leneol:] == eol:
				break
		else:
			break
	return bytes(line)

class FlukeError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Fluke:
	def __init__(self, portNum, name):
		self._port = serial.Serial(portNum, baudrate=115200, timeout=.1, writeTimeout=0)
		self._name = name
		try:
			result = self.__cmd("ID")
		except FlukeError as e:
			self._port.close()
			self._port = serial.Serial(portNum, baudrate=9600, timeout=.1, writeTimeout=0)
			result = self.__cmd("ID")
		self._model = result.split(',')[0]
		#print(name + " is a " + self._model)
	
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		self._port.close()

	def __readline(self):
		eol = b'\r'
		leneol = len(eol)
		line = bytearray()
		while True:
			c = self._port.read(1)
			if c:
				line += c
				if line[-leneol:] == eol:
					break
			else:
				break
		return bytes(line)

	def __cmd(self, command):
		cmd_ack = 'no err'
		for x in range(0,5):
			self._port.write(command + '\r')
			cmd_ack = self.__readline().rstrip('\r')
			#print("CMD_ACK: '" + str(cmd_ack) + "'")
			if (cmd_ack == '0'):
				response = self.__readline().rstrip('\r')
				return response
		raise FlukeError(cmd_ack)
	
	# Poll a Fluke device for current data point
	def poll(self):
		items = {0:(self._name, '')}

		# Query for the current value
		result = self.__cmd("QM")
		valueIdx = 0
		if (self._model == "FLUKE 189"):
			# 189 responds with the command repeated first
			valueIdx = 1
		# Use regex to find number portion of the response
		p = re.compile(r'[^\d-]*(-?[\d]+(\.[\d]*)?([eE][+-]?[\d]+)?)')
		m = p.match(result.split(',')[valueIdx])
		if m:
			value = float(m.groups()[0])
		items[0] = self._name, value
		#print(items)
		return items

	def getParamNames(self):
		return [self._name]


if __name__ == "__main__":
    args = docopt(__doc__, version='fluke 1.0')

    dev = Fluke(args['--port'], "dev")
    
    value = float(dev.poll()[0][1])
    scale = 1.0
    
    if args['--scale'] is not None:
        try:
            scale = float(args['--scale'])
        except ValueError:
            print(args['--scale'] + " is not a number", file=sys.stderr)
    value = value * scale
    
    if args['--round']:
        value = round(value, int(args['--round']))
        if int(args['--round']) <= 0:
            value = int(value)
    
    sys.stdout.write(str(value))
