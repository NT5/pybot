#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import socket, time, threading, util as util

class BanchoNet:	
	def __init__(self, nick, password, channels, server, port, sender, start = False):
		self.nick = nick
		self.password = password
		self.channels = channels
		self.server = server
		self.port = port
		self.sender = sender
		self.running = True
		self.limiter = { 'allowance': 3, 'rate': 3, 'per': 1, 'last_check': int( time.time() ) }
		if start == True: self.start()
	
	def start(self):
		try:
			self.irc = socket.socket()
			self.irc.settimeout(1200)
			self.irc.connect((self.server, self.port))
			self.irc.send('PASS %s\r\n' % self.password)
			self.irc.send('USER %s 0 * :NT5 Python Bot\r\n' % (self.nick))
			self.irc.send('NICK %s\r\n' % self.nick)
			print("[+] BanchoNet connect as %s in %s" % ( self.nick, ", ".join(self.channels) ))
			
			while self.running:
				try: data = self.irc.recv(4096).decode("UTF-8")
				except: data = self.irc.recv(4096)
				if len( data ) == 0 and self.running:
					print "[-] BanchoNet Reconnecting...."
					self.reconnect()
					break
				else:
					lines = data.split("\n")
					for line in lines:
						line = unicode(line).strip()
						if line == '':
							continue
						self.IrcListen(line)
			print "[-] BanchoNet Stopped"
		except Exception, e:
			print("[-] Error on BanchoNet connection! - %s" % e )
			if self.running: self.reconnect()
	
	def IrcListen(self, data):
		#print data
		try: event = data.split(' ')[1]
		except: event = None
			
		if data.split(' ')[0] == 'PING':
			self.irc.send('PONG %s :TIMEOUTCHECK\r\n' % self.server)

		if event == '001':
			for chan in self.channels:
				self.Join( chan )

		if event == 'JOIN':
			user = util.GetNick( data )
			for loc in self.sender:
				if user in loc.assets['config']['bancho_listen']:
					for chan in loc.assets['config']['bancho_listen'][user]:
						if loc.idle['chan'].get(chan):
							if int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
								loc.message( "13[Osu!] [10%s13]14 %s" % (user, "User Online"), chan, show = False )
		
		if event == 'QUIT':
			user = util.GetNick( data )
			for loc in self.sender:
				if user in loc.assets['config']['bancho_listen']:
					for chan in loc.assets['config']['bancho_listen'][user]:
						if loc.idle['chan'].get(chan):
							if int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
								loc.message( "13[Osu!] [10%s13]14 %s" % (user, "User Offline"), chan, show = False )
		
		if event == 'PRIVMSG':
			user = util.GetNick( data )
			chan = util.GetChannel( data )
			try:
				text = util.NoIrcColors( data[1:].split(':',1)[1] )
				action = util.GetMessageAction( text )
				if action: text = action
			except:
				pass
		
			#Editable
			for loc in self.sender:
				if user in loc.assets['config']['bancho_listen']:
					for chan in loc.assets['config']['bancho_listen'][user]:
						if loc.idle['chan'].get(chan):
							if int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
								loc.message( "13[Osu!] [10%s13]14 %s" % (user, text), chan, show = False )
			#for loc in self.sender:
			#	loc.message( "%s: %s" % ( user, text), loc.channels[0] )
					
	def reconnect(self):
		if self.running:
			try:
				try: self.irc.shutdown(1)
				except: pass
				time.sleep(25)
				self.start()
			except Exception, e:
				print "[-] Can't connect to bancho, trying again..."
				time.sleep(30)
				self.reconnect()
	
	def Join( self, chan ):
		self.send("JOIN %s" % chan)
		
	def send( self, msg ):
		msg = u"%s\r\n" % msg
		self.irc.send(msg.encode('utf-8'))
	
	def message(self, msg, chan):
		current = int( time.time() )
		time_passed = (current - self.limiter['last_check'])
		self.limiter['last_check'] = current
		self.limiter['allowance'] += time_passed * (self.limiter['rate'] / self.limiter['per'])
		
		if self.limiter['allowance'] > self.limiter['rate']:
			self.limiter['allowance'] = self.limiter['rate']
		
		if self.limiter['allowance'] < 1: 
			timer = threading.Timer(2.5, self.message, [msg, chan])
			timer.start()
		else:
			self.limiter['allowance'] -= 1
			self.send( "PRIVMSG %s :%s" % ( chan, msg[:450]) )
			if len(msg) > 450:
				self.message( msg[450:], chan )
	
	def quit(self, rq = "Shutdown"):
		self.send("QUIT %s" % rq)
		print "[-] BanchoNet Quit: %s" % rq

