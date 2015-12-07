import datetime
import subprocess
from catnet.turning import stop, turn_clockwise, turn_c_clockwise
from catnet.compass import get_bearing
import RPi.GPIO as GPIO
import RPIO
import time

GPIO_list = [18, 23, 24, 25]

#make a list of GPIO sensors and the angles they correspond to:

def start_overwatch():

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


    # Function for what to do on motion, wrapped in a fail safe
    in_motion = [False]
    def motion_detected(active_sensor, value):
        if in_motion[0]:
            return
        in_motion[0] = True
        try:
            print "motion detected on {}".format(active_sensor)
            motion_angle = GPIO_sensor[active_sensor]

            while True:

                bearing_angle = get_bearing()
                difference = abs(bearing_angle - motion_angle)

                if difference < 20:
                    stop()
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
                        turn_clockwise()
                    else:
                        turn_c_clockwise()

        finally:
            stop()
            in_motion[0] = False

    #setup wait for interupts
    for pin_number in GPIO_sensor.keys():
        print "Setting up sensor {}".format(pin_number)
        RPIO.add_interrupt_callback(pin_number, threaded_callback=True, callback=motion_detected, edge="rising")

    #wait for interupts in try for GPIO cleanup
    try:
        RPIO.wait_for_interrupts()
    finally:
        GPIO.cleanup()

