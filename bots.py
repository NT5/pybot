#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import json, threading, sys, time
from res.IrcBot import IrcBot
from res.banchonet import BanchoNet
from res.OsunpServer import OsunpServer

try: config_file = sys.argv[1]
except: config_file = 'bot.json'

try: Bots_config = json.loads( open( config_file ).read() )
except Exception, e:
	print "Bot File error: " + str( e )
	sys.exit()
	
#MainBots
Bots = []
for Bot in Bots_config['Bots']:
	try:
		print "Loading %s on %s:%i..." % (Bot['nick'], Bot['server'], Bot['port'])
		Bots.append( IrcBot( Bot['nick'], Bot['password'], Bot['channels'], Bot['server'], Bot['sv_pass'], Bot['port'], Bot['path'] ) )
		assets = None
		thr = threading.Thread(target=Bots[len(Bots)-1].start)
		thr.setDaemon(True)
		thr.start()
	except Exception, e:
		print "[-] Can't create BOT %s " % str(e)
		
#BanchoNet
if Bots_config.get("BanchoNet"):
	_BanchoNet = BanchoNet(Bots_config['BanchoNet']['nick'], Bots_config['BanchoNet']['token'], Bots_config['BanchoNet']['channels'], Bots_config['BanchoNet']['server'], Bots_config['BanchoNet']['port'], Bots)
	thr = threading.Thread( target=_BanchoNet.start )
	thr.setDaemon(True)
	thr.start()
	#Injection
	for x in Bots:
		x.setbancho(_BanchoNet)
	print "[+] BanchoNet Injected!"

#Osu!np
if Bots_config.get("OsunpSever"):
	thr = threading.Thread( target=OsunpServer, args=(Bots_config['OsunpSever']['port'], Bots,))
	thr.setDaemon(True)
	thr.start()

thr = None
rq = raw_input("")

for x in Bots:
	try: x.quit("Stopped from console %s" % u"("+rq+")" if rq else "Stopped from console " )
	except: print "[%s] Stopped from console (no quit send)" % x.nick