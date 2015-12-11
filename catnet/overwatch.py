from catnet.turning import stop, turn_clockwise, turn_c_clockwise
from catnet.compass import get_bearing
import RPi.GPIO as GPIO
import time

GPIO_list = [18, 23, 24, 25]

def start_overwatch():
    #make a list of GPIO sensors and the angles they correspond to:
    GPIO_sensor = {}

    def calibrate(sensor):
        raw_input("turn to face {} and then press enter".format(sensor))
        return get_bearing()

    print "calibration step"

    for sensor in GPIO_list:
        GPIO_sensor[sensor] = calibrate(sensor)
        print "{} is {}".format(sensor, GPIO_sensor[sensor])
    raw_input("turn to desired start point, then press enter")


    #setup the GPIO pins as inputs:
    GPIO.setmode(GPIO.BCM)
    for sensor in GPIO_sensor.keys():
        GPIO.setup(sensor, GPIO.IN)

    # motion detection function
    def motion_detected(active_sensor):
        motion_angle = GPIO_sensor[active_sensor]
        while True:

            bearing_angle = get_bearing()
            difference = abs(bearing_angle - motion_angle)

            if difference < 10:
                stop()
                print "turned to {}".format(bearing_angle)
                time.sleep(3)
                break
            elif bearing_angle > motion_angle:
                # Motion is anti-clockwise of bearing.
                if bearing_angle - motion_angle < 180:
                    turn_c_clockwise()
                else:
                    turn_clockwise()
            else:
                # Motion is clockwise of bearing.
                if motion_angle - bearing_angle < 180:
                    turn_c_clockwise()
                else:
                    turn_clockwise()

    #poll motion sensors
    try:
        while True:
            for sensor in GPIO_list:
                if GPIO.input(sensor) == True:
                    print "motion detected on sensor {}".format(sensor)
                    motion_detected(sensor)
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

