import time
import datetime
import subprocess
from collections import OrderedDict
from turn_module import stop_pulse, c_pulse, cc_pulse
from compus_module import get_bearing
import RPi.GPIO as GPIO
import RPIO
import threading

def start_overwatch():
    try:
        #GPIO setup with relative headings

    	GPIO.setmode(GPIO.BCM)

    	GPIO_sensors = OrderedDict([
    		(23, 0),
    		(24, 90),
    		(25, 180),
    		(18, 270),
    	])

    	for sensor in GPIO_sensors.keys():
    		GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        #Calibrate compuss heading to relative heading

    	angle_offset = get_bearing()
    	print angle_offset

        #Create a variable called daemon running, and a global set
    	daemon_running = False
    	motion_set = set()

        #Function for reading motion_set and working out the correct angle to turn
    	def motion_bearing():
    		motion_bearing = []
    		for sensor, angle in GPIO_sensors.items():
    			if sensor in motion_set:
    				motion_bearing.append(angle)
    		bearing = sum(motion_bearing)/len(motion_bearing)
    		if bearing > 360:
    			bearing = bearing - 360
    		return bearing

        #Function for activating turret
    	def turret(target_bearing):
    		while True:
    			current_bearing = get_bearing() - angle_offset
    			if current_bearing < 0:
    				current_bearing = current_bearing + 360
    			print current_bearing
    			if current_bearing - target_bearing > 10:
    				cc_pulse()
    			elif current_bearing - target_bearing < -10:
    				c_pulse()
    			else:
    				stop_pulse()
    				break
    			time.sleep(0.02)

        #take picture function
    	def take_snap():
    		time.sleep(1)
    		file_name = (datetime.datetime.now()).strftime('%Y-%m-%d-%H-%M-%S')
    		subprocess.call('fswebcam --device v4l2:/dev/video0 --input 0 --resolution 320x240 --skip 100 --jpeg 80 /home/jenny/test/image-{}.jpg'.format(file_name), shell=True)
    		print "picture taken"

        #Daemon thread
    	def activate_turret():
    		global daemon_running
    		time.sleep(0.5)
    		print "daemon waking after sleep"
    		print motion_set
    		bearing = motion_bearing()
    		print bearing
    		turret(bearing)
    		take_snap()
    		daemon_running = False
    		print "daemon died"


    	def motion_detected(gpio, x):
    		global motion_set, daemon_running
    		print "motion detected"
    		if daemon_running == True:
    			print "adding to daemon"
    			motion_set.add(gpio)
    		elif daemon_running == False:
    			print "starting daemon"
    			motion_set = set()
    			motion_set.add(gpio)
    			daemon_running = True
    			d = threading.Thread(target=activate_turret)
    			d.setDaemon(True)
    			d.start()


    	for pin_number in GPIO_sensors.keys():
    		RPIO.add_interrupt_callback(pin_number, callback=motion_detected)

    	RPIO.wait_for_interrupts()

    finally:
    	stop_pulse()
    	GPIO.cleanup()

