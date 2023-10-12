#!/bin/python3

#first written: Ago 2021
import subprocess
import json
from threading import Timer
import time
from time import sleep
temp_command = "cat"
temp_args = "/sys/class/thermal/thermal_zone0/temp"

data = []
intervallo_totale = 60 * 10
intervallo_acquisizione = 1
final_data = None

def getTemp():
	result = subprocess.run([temp_command, temp_args], stdout=subprocess.PIPE)
	#print(result.stdout)
	return int(result.stdout.decode("utf-8"))

def calculateAverage():
	size = len(data)
	x = 0
	for i in data:
		x = x + i
	return x / size

def prettyTemp(value):
	return value/1000.0


def saveData():
	t_media = calculateAverage()
	t_media = prettyTemp(t_media)
	time_ = time.asctime().replace(" ", "_").replace(":", "__")
	struct = {
		"time": time_,
		"t_media" : t_media,
		"acquisition_interval" : intervallo_acquisizione,
		"total_interval": intervallo_totale,
		"temperature" : data,
	}
	filename = time_ +"_temperature.json"
	#json = json.dumps(struct)
	with open(filename, "w") as file:
		json.dump(struct, file)

def acquireData():
	temp = getTemp()
	data.append(temp)
	print(prettyTemp(temp))

class RepeatedTimer(object):
	def __init__(self, interval, function, *args, **kwargs):
		self.timer = None
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False



print("Start monitoring...")
acquireData()
rt = RepeatedTimer(intervallo_acquisizione, acquireData)

try:
	sleep(intervallo_totale)
	saveData()
finally:
	rt.stop()
