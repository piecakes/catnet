from catnet.adafruit.pwm import PWM

pwm = PWM(0x40)
pwm.setPWMFreq(60)

def stop():
  pwm.setPWM(0, 0, 0)

def turn_clockwise():
  pwm.setPWM(0, 0, 395)

def turn_c_clockwise():
  pwm.setPWM(0, 0, 404)

