import wifi
from http_client import *
import database

def new_messages():
	lastseq = str(db.get('msgseq'))
	url = 'http://'+server+':9000/unread/'+id+'?lastseq='+lastseq
	msgcount = get(url).text
	if msgcount == '0':
		return None
	else:
		return int(msgcount)

wifi.connect()
id = str(ubinascii.hexlify(pyb.unique_id()), 'ascii')
db = database.Database()
server = 'imaclocal.sammachin.com'
