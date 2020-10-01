import requests
import ast
import time
import re
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

L_pin = 27
R_pin = 23
C_pin = 4
U_pin = 17
D_pin = 22

A_pin = 5
B_pin = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up

RST = None

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)

padding = -2
top = padding
bottom = height-padding

x = 0

font = ImageFont.load_default()

pages = 3
currentpage = 0
currenttime = 0
disabledisplay = False


def getstats():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    r = requests.get('http://192.168.200.16:8080/', headers=headers)
    stats = ast.literal_eval(r.text)
    return stats


def displaycpu(cpu):
    draw.text((x, top), '0: ' + str(cpu[0]) + '%', font=font, fill=255)
    draw.text((x+60, top), '1: ' + str(cpu[1]) + '%', font=font, fill=255)
    draw.text((x, top+8), '2: ' + str(cpu[2]) + '%', font=font, fill=255)
    draw.text((x+60, top+8), '3: ' + str(cpu[3]) + '%', font=font, fill=255)
    draw.text((x, top+16), '4: ' + str(cpu[4]) + '%', font=font, fill=255)
    draw.text((x+60, top+16), '5: ' + str(cpu[5]) + '%', font=font, fill=255)
    draw.text((x, top+24), '6: ' + str(cpu[6]) + '%', font=font, fill=255)
    draw.text((x+60, top+24), '7: ' + str(cpu[7]) + '%', font=font, fill=255)
    draw.text((x, top+32), '8: ' + str(cpu[8]) + '%', font=font, fill=255)
    draw.text((x+60, top+32), '9: ' + str(cpu[9]) + '%', font=font, fill=255)
    draw.text((x, top+40), '10: ' + str(cpu[10]) + '%', font=font, fill=255)
    draw.text((x+60, top+40), '11: ' + str(cpu[11]) + '%', font=font, fill=255)


def displayram(ram):
    draw.text((x, top+48), "Memory: " + str(ram[1]) + 'GB/' + str(ram[0]) + 'GB', font=font, fill=255)


def displaydisks(disks):
    for i in range(numdevices):
        draw.text((x, top+(8*i)), str(devices[i]) + ': ' + str(disks['used_%s' % devices[i]]) + 'GB/' + str(disks['size_%s' % devices[i]]) + 'GB', font=font, fill=255)


def displaytime():
    current_time = time.strftime('%I:%M:%S %p')
    current_date = time.strftime('%a, %d %b %Y')
    draw.text((x, top), current_time, font=font, fill=255)
    draw.text((x, top+8), current_date, font=font, fill=255)



while True:
    if currenttime % 18 == 0:
        stats = getstats()
        currenttime = 0

    if not GPIO.input(R_pin):
        currentpage += 1
        if currentpage > pages-1:
            currentpage = 0

    if not GPIO.input(L_pin):
        currentpage -= 1
        if currentpage < 0:
            currentpage = pages-1

    if not GPIO.input(A_pin) and not GPIO.input(B_pin):
        disabledisplay = not disabledisplay

    cpu = []
    for i in range(0, 12):
        cpu.append(stats['cpu_%s' % i])
    ram_total = round(stats['total_mem'], 1)
    ram_free = round(stats['free_mem'], 1)
    ram = [ram_total, ram_free]

    numdevices = stats['numdisks']
    devices = []
    disks = {}
    for key in stats:
        if key.startswith('size'):
            devices.append(re.search('(size_)(\w+:\\\\)?', key).group(2))

    for device in devices:
        disks['size_%s' % device] = round(stats['size_%s' % device], 1)
        disks['used_%s' % device] = round(stats['used_%s' % device], 1)

    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    if currentpage == 0 and not disabledisplay:
        displaycpu(cpu)
        displayram(ram)
    elif currentpage == 1 and not disabledisplay:
        displaydisks(disks)
    elif currentpage == 2 and not disabledisplay:
        displaytime()

    if not disabledisplay:
        draw.text((x, top+56), 'Page: ' + str(currentpage), font=font, fill=255)

    disp.image(image)
    disp.display()

    time.sleep(0.1)
    currenttime += 1
