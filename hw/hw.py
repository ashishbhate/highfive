#!/usr/bin/python3
import sys
import time
import threading

import adafruit_pcd8544
import board
import busio
import digitalio
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont 

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use BCM pin numbering that adafruit_pcd8544 already sets

SERVO_PIN = 18 # GPIO-1
GPIO.setup(SERVO_PIN, GPIO.OUT) # set a port/pin as an output   
servo = GPIO.PWM(SERVO_PIN,50)  # servo, pulse 50Hz
servo.start(0)

IR_PIN = 17 # GPIO-0
GPIO.setup(IR_PIN, GPIO.IN)

# DISPLAY
BORDER = 2
FONTSIZE = 10

# Initialize Display SPI bus and control pins
spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
print(spi.frequency)
dc = digitalio.DigitalInOut(board.D22)  # data/command
cs = digitalio.DigitalInOut(board.CE1)  # Chip select
reset = digitalio.DigitalInOut(board.D24)  # reset

display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)
display.bias = 4
display.contrast = 125
backlight = digitalio.DigitalInOut(board.D23)  # backlight
backlight.switch_to_output()


def calm():
   servo.ChangeDutyCycle(0)

def to_angle(angle):
   servo.ChangeDutyCycle(2+(angle/18))
   # stability
   #time.sleep(0.5)
   #servo.ChangeDutyCycle(0)

def arm_high():
    to_angle(100)

def arm_low():
    to_angle(20)

def arm_mid():
    to_angle(90.0)

def SetupHighFive():
    arm_low()
    time.sleep(0.5)
    arm_high()
    time.sleep(0.5)
    wave()

def wave():
    arm_mid()
    time.sleep(0.2)
    arm_high()
    time.sleep(0.2)
    arm_mid()
    time.sleep(0.2)
    arm_high()
    time.sleep(0.2)
    calm()

def cleanup():
    servo.stop()
    display.fill(0)
    display.show()
    backlight.value = False
    GPIO.cleanup()


arm_lock = threading.Lock()

if len(sys.argv) < 2:
    name = "Someone"
else:
    name = sys.argv[1]

# Turn on the Backlight LED
backlight.value = True

display.fill(0)
display.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (display.width, display.height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black background
draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)
 
# Draw a smaller inner rectangle
draw.rectangle(
    (BORDER, BORDER, display.width - BORDER - 1, display.height - BORDER - 1),
    outline=0,
    fill=0,
)

text = f"{name}\nsent a\nhigh five!"

# Load a nicer font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", FONTSIZE)

# Draw Some Text
draw.multiline_text(
    (5,5),
    text,
    font=font,
    fill=255,
)
 
# Display image
image = image.rotate(angle=180)
display.image(image)
display.show()

# Wave arm
with arm_lock:
    SetupHighFive()

# Process High Five
def handle_high_five(_):
    with arm_lock:
        arm_low()
        time.sleep(0.2)
        cleanup()
        sys.exit(0)

# Detect High Five
GPIO.add_event_detect(IR_PIN, GPIO.FALLING, handle_high_five, 2000)

# Demand high five
while True:
    time.sleep(5)
    with arm_lock:
        wave()