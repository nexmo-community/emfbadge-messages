### Category: Comms 
### Author: Sam Machin - Nexmo
### License: MIT
### Appname: Messages
### Description: Receive Messages



import wifi
import mqtt
import ugfx
import pyb
import os
import math
import time
import database
import buttons
from http_client import *
import ubinascii
import json

def callback(topic, msg):
	data = json.loads(msg)
	inbox.set(data['sequence'], msg)
	
	if data['sequence'] == 1:
		db.set('msgseq', data['sequence'])
		lastseq = 0
	else:
		lastseq = db.get('msgseq')
	if data['sequence'] - lastseq > 1:
		c.publish('resend/'+id, str(lastseq))
		return
	else:
		db.set('msgseq', data['sequence'])
	if data['type'] == 'message':
		printmsg(data['sender'], data['payload'], data['ts'])
	else:
		print(data)
	db.flush()
	inbox.flush()


		
def zf(d):
	l=2
	if len(d) < l:
		return "0" + d
	else:
		return d
		
def timestring(tt):
	offset = 946681200
	t = tt-offset
	ts = time.localtime(t)
	timestamp = "{}:{}:{} {}/{}/{}".format(zf(str(ts[3])), zf(str(ts[4])), zf(str(ts[5])), str(ts[2]), str(ts[1]), str(ts[0]))
	return timestamp


def display():
	logo = 'apps/nexmo~messages/nexmo_logo.gif'
	ugfx.area(0,0,ugfx.width(),ugfx.height(),0xFFFF)
	ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)	
	ugfx.text(20,20,"My Number is...",ugfx.BLACK)
	ugfx.text(20,130,"Powered By, ",ugfx.GREY)
	ugfx.display_image(15,150,logo)
	ugfx.set_default_font(ugfx.FONT_TITLE)
	ugfx.text(40,75,mynumber+" ",ugfx.BLUE)
	

def printmsg(sender, text, ts):
	ugfx.set_default_font(ugfx.FONT_SMALL)	
	ugfx.area(0,0,ugfx.width(),ugfx.height(),0x0000)
	ugfx.text(10,10,"From: "+sender,ugfx.BLUE)
	timestamp = timestring(ts)
	linelen = 40
	lines = int(math.ceil(len(text)/linelen))
	for l in range(0, lines):
		pixels = l*25+35
		start = l*linelen
		end = l*linelen+linelen
		if end>len(text):
			end = len(text)
		linetext = text[start:end]
		ugfx.text(10,pixels,linetext,0xFFFF)
	ugfx.text(10,200,timestamp,ugfx.GREEN)
	return
	

def viewmsg():
	msgid = db.get('msgseq')
	msg = inbox.get(msgid)
	if msg == None:
		ugfx.set_default_font(ugfx.FONT_SMALL)	
		ugfx.area(0,0,ugfx.width(),ugfx.height(),0x0000)
		ugfx.text(40,100,"NO MESSAGES",ugfx.BLUE)
		pyb.delay(1000)
		return
	else:
		data = json.loads(msg)
		printmsg(data['sender'], data['payload'], data['ts'])
	while True:
		if buttons.is_triggered("JOY_UP"):
			print(msgid)
			msgid -= 1
			msg = inbox.get(msgid)
			if msg != None:
				data = json.loads(msg)
				printmsg(data['sender'], data['payload'], data['ts'])
			else:
				msgid += 1
		if buttons.is_triggered("JOY_DOWN"):
			print(msgid)
			msgid += 1
			msg = inbox.get(msgid)
			if msg != None:
				data = json.loads(msg)
				printmsg(data['sender'], data['payload'], data['ts'])
			else:
				msgid -= 1
		if buttons.is_triggered("BTN_B"):
			display()
			return

def check():
	try:
		c.check_msg()
	except:
		pyb.delay(100)
		
def myNumber():
	global mynumber
	url = 'http://'+server+'/number/'+id
	if mynumber == None:
		mynumber = get(url).text
	return mynumber

def reset():
	lastseq = db.get('msgseq')
	for x in range(1,lastseq+1):
		inbox.delete(x)
	db.set('msgseq', 0)
	global myNumber
	mynumber = None
	inbox.flush()
	db.flush()
	


def connect_mqtt():
    global c
    c = mqtt.MQTTClient(id, server)
    try:
        c.connect()
    except OSError:
        pyb.delay(200)
        connect_mqtt()
        return
    c.set_callback(callback)
    c.subscribe('/badge/'+id+'/msg', qos=0)
	
def disconnect_mqtt():
    global c
    if c:
        try:
            c.disconnect()
        except:
            pass

def connect(reconnect=False):
    global c
    ugfx.clear(ugfx.BLUE)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(0, 10, "Connecting to Wifi...", ugfx.WHITE)
    if reconnect:
        disconnect_mqtt()
        wifi.nic().disconnect()
    while not wifi.is_connected():
        try:
            wifi.connect(wait=True, timeout=15)
        except:
            pyb.delay(200)
    ugfx.text(0, 22, "Connecting to MQTT...", ugfx.WHITE)
    c = None
    connect_mqtt()

def warning():
	ugfx.clear(ugfx.BLUE)
	ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
	ugfx.text(30, 10, "WARNING!!!", ugfx.RED)
	ugfx.set_default_font(ugfx.FONT_SMALL)
	ugfx.text(30, 40, "Messages are recieved over an ", ugfx.WHITE)
	ugfx.text(30, 55, "unsecured connection, the text ", ugfx.WHITE)
	ugfx.text(30, 70, "and senders number may be visable ", ugfx.WHITE)
	ugfx.text(30, 105, "Press A to accept and continue ", ugfx.WHITE)
	while True:
		if buttons.is_triggered('BTN_A'):
			ugfx.clear()
			return


#Check and Connect to WiFi
if wifi.is_connected():
	pass
else:
	wifi.connect()

#Init GFX and Buttons
ugfx.init()
buttons.init()

#Setup Databases
db = database.Database()
inbox = database.Database(filename='inbox.json')

#Server Address
server = 'badge.sammachin.com'

#Get CPU ID
id = str(ubinascii.hexlify(pyb.unique_id()), 'ascii')

#Get MSISDN
mynumber = None
myNumber()

# Setup Sequence ID If First run show Warning
if db.get('msgseq') == None:
	warning()
	db.set('msgseq', 0)
	db.flush()
else:
	pass


#Connect MQTT
connect()

#Check for unread messages
lastseq = db.get('msgseq')
url = 'http://%s/resend/%s?lastseq=%s' % (server, id, lastseq)
resend = get(url).text

#Main Screen and Watch for Input/Messages
display()
next_tick = 0
while True:
	if buttons.is_triggered('BTN_A'):
		viewmsg()
	if buttons.is_triggered('BTN_B'):
		display()
	if pyb.millis() > next_tick:
		if not wifi.is_connected():
			connect(reconnect=True)
		try:
			c.check_msg()
		except:
			pass
		try:
			c.sock.send(b"\xc0\0")  # ping
		except:
			connect(reconnect=True)
			display()
		next_tick = pyb.millis() + 30000
	try:
		c.check_msg()
	except:
		pyb.delay(200)

ugfx.clear()

		
	
 
