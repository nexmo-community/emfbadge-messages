from http_client import *
import database
import ubinascii
import ugfx

update_rate = 15

id = str(ubinascii.hexlify(pyb.unique_id()), 'ascii')
db = database.Database()
server = 'badge.sammachin.com'

def periodic_home(icon):
	lastseq = str(db.get('msgseq'))
	url = 'http://'+server+':9000/unread/'+id+'?lastseq='+lastseq
	try:
		msgcount = get(url).text
	except:
		return ''
	if msgcount == '0':
		return ''
	else:
		icon.show()
		ugfx.set_default_font("c*")
		icon.area(0,0,icon.width(),icon.height(),ugfx.BLUE)
		icon.text(4,4,msgcount+" ",0xFFFF)
		if msgcount == '1':
			return msgcount + " Unread Message"
		else:
			return msgcount + " Unread Messages"
		
	
	
