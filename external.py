from http_client import *
import database
import ubinascii
import ugfx

needs_wifi = True
update_rate = 120 * 1000
needs_icon = True


id = str(ubinascii.hexlify(pyb.unique_id()), 'ascii')
db = database.Database()
server = 'badge.sammachin.com'

def tick(icon):
	lastseq = db.get('msgseq')
	if not lastseq:
		return
	url = 'http://%s/unread/%s?lastseq=%s' % (server, id, lastseq)
	print(url)
	msgcount = get(url).text
	if msgcount == '0':
		return ''
	else:
		icon.show()
		ugfx.set_default_font("c*")
		icon.area(0,0,icon.width(),icon.height(),ugfx.BLUE)
		icon.text(4,4,msgcount+" ",0xFFFF)
		if msgcount == '1':
			return  "1 Unread Message"
		else:
			return msgcount + " Unread Messages"