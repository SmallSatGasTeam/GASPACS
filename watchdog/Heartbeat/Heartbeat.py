import RPi.GPIO as GPIO
import asyncio

# this is the heart beat code. objectives are:
# 1) A function that sends one pulse
#   A)


def setUp():

    GPIO.setwarnings(False)

    # Use physical pin numbering
    GPIO.setmode(GPIO.BCM)

    # Set pin 40(BCM 21) to be an output pin and set initial value to low (off)
    GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)




async def longTap():
    waitTime = 4
    setUp()
    while True:
        # send a pulse
        GPIO.output(21, GPIO.HIGH)
        await asyncio.sleep(waitTime/2)
        GPIO.output(21, GPIO.LOW)
        # wait a four seconds.
        await asyncio.sleep(waitTime/2)
