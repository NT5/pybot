#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import json, threading, sys, time
import res.util as util
from res.IrcBot import IrcBot
from res.banchonet import BanchoNet
from res.OsunpServer import OsunpServer
from res.LastFMNP import NpLastFM

_launch_vars = {}
for prev, item, next in util.neighborhood( sys.argv ):
	if item[:1] == "-": _launch_vars.setdefault( item[1:], next )

try: Bots_config = json.loads( open( "bot.json" if _launch_vars.get('config') == None else _launch_vars['config'] ).read() )
except Exception, e:
	print "Bot File error: " + str( e )
	sys.exit()
	
#MainBots & vars
Bots = []
Threads = []
_BanchoNet = None
_LastFM = None
_OsuNPS = None

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
	_OsuNPS = OsunpServer(Bots_config['OsunpSever']['port'], Bots)
	Threads.append( threading.Thread( target=_OsuNPS.start ) )
	
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
	time.sleep(0.5)
print "[+] %i Threads running" % len( Threads )

#Keeps all active
rq = raw_input("")

"""Stopping all things"""

#Bots
for bot in Bots:
	bot.running = False
	try: bot.quit("Stopped from console %s" % u"("+rq+")" if rq else "Stopped from console " )
	except: print "[%s] Stopped from console (no quit send)" % bot.nick
	
#BanchoNet
if _BanchoNet:
	_BanchoNet.running = False
	_BanchoNet.quit()

#Osu!np
if _OsuNPS: _OsuNPS.stop()
	
#LastFM
if _LastFM: _LastFM.stop()

print "Waiting for all threads finish..."

for thr in Threads: thr.join(60)

print "Script close successful"
sys.exit()