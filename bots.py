#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import json, threading, sys, time
from res.IrcBot import IrcBot
from res.banchonet import BanchoNet
from res.OsunpServer import OsunpServer
from res.LastFMNP import NpLastFM

try: config_file = sys.argv[1]
except: config_file = 'bot.json'

try: Bots_config = json.loads( open( config_file ).read() )
except Exception, e:
	print "Bot File error: " + str( e )
	sys.exit()
	
#MainBots & vars
Bots = []
Threads = []
_BanchoNet = None
_LastFM = None

for Bot in Bots_config['Bots']:
	try:
		print "Loading %s on %s:%i..." % (Bot['nick'], Bot['server'], Bot['port'])
		Bots.append( IrcBot( Bot['nick'], Bot['password'], Bot['channels'], Bot['server'], Bot['sv_pass'], Bot['port'], Bot['path'] ) )
		Threads.append(threading.Thread(target=Bots[len(Bots)-1].start))
		
	except Exception, e:
		print "[-] Can't create BOT %s " % str(e)
		
#BanchoNet
if Bots_config.get("BanchoNet"):
	_BanchoNet = BanchoNet(Bots_config['BanchoNet']['nick'], Bots_config['BanchoNet']['token'], Bots_config['BanchoNet']['channels'], Bots_config['BanchoNet']['server'], Bots_config['BanchoNet']['port'], Bots)
	Threads.append( threading.Thread( target=_BanchoNet.start ) )

#Osu!np
if Bots_config.get("OsunpSever"):
	Threads.append( threading.Thread( target=OsunpServer, args=(Bots_config['OsunpSever']['port'], Bots,)) )
	
#LastFM
if Bots_config.get("LastFM"):
	_LastFM = NpLastFM( Bots_config['LastFM']['key'], Bots )
	Threads.append( threading.Thread( target=_LastFM.run ) )

#Injection
for x in Bots:
	if _BanchoNet:
		x._banchonet = _BanchoNet
		print "[%s] [+] BanchoNet Injected" % x.nick
	if _LastFM:
		x._lastfm = _LastFM
		print "[%s] [+] LastFM Injected" % x.nick

#Start all Threads
for thr in Threads:
	thr.setDaemon(True)
	thr.start()
	time.sleep(1)
print "[+] %i Threads running" % len( Threads )

#Keeps all active
rq = raw_input("")

#Quit Bots
for x in Bots:
	try: x.quit("Stopped from console %s" % u"("+rq+")" if rq else "Stopped from console " )
	except: print "[%s] Stopped from console (no quit send)" % x.nick

sys.exit()