#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

#Modules
import socket, threading, sys, gc, time, json
from colorama import init as ColoramaInit, Fore, Back, Style
import util as util
from commands import onCommand, onModCommand

#Colorama Config
ColoramaInit()
COLOR = { 'black': Fore.BLACK, 'red': Fore.RED, 'green': Fore.GREEN, 'yellow': Fore.YELLOW, 'blue': Fore.BLUE, 'magenta': Fore.MAGENTA, 'cyan': Fore.CYAN, 'white': Fore.WHITE }

class IrcBot:
	version = '0.3.3 beta build 16'
	
	def __init__(self, nick, password, channels, server, sv_pass, port, path):
		self.nick = nick
		self.password = password
		self.channels = channels
		self.server = server
		self.sv_pass = sv_pass
		self.port = port
		self.path = path
		self.running = True
		self.assets = {}
		self.names = {}
		self.netname = "unknown"
		self.idle = { "chan": { } }
		self.uptime = { "server": 0, "script": int( time.time() ) }
		self.LoadAssets()
		self._banchonet = None
		self._lastfm = None
		self.cleverbot = { "type": 1, "users": {} }
		self.flood = {}
		self.limiter = { 'messages': { 'allowance': 15, 'rate': 15, 'per': 1, 'last_check': int( time.time() ) }, 'commands': {  } }
		
	def start(self):
		try:
			self.irc = socket.socket()
			self.irc.settimeout(1200)
			self.irc.connect((self.server, self.port))
			self.irc.send('PASS %s\r\n' % self.sv_pass)
			self.irc.send('USER %s 0 * :NT5 Python Bot %s\r\n' % (self.nick, self.version))
			self.irc.send('NICK %s\r\n' % self.nick)
			self.uptime['server'] = int( time.time() )
			self.c_print("%s[+] Bot started" % ( COLOR['blue'] ))
			
			while self.running:
				try: data = self.irc.recv(1204).decode("UTF-8")
				except: data = self.irc.recv(1204)
				if len( data ) == 0 and self.running:
					self.c_print("%s%-s" % ( COLOR['red'], "Server Closed the connection." ) )
					self.c_print("%s%-s" % ( COLOR['blue'], "[+] Reconnecting...." ))
					self.reconnect()
					break
				else:
					lines = data.split("\n")
					for line in lines:
						line = unicode(line).strip()
						if line == '':
							continue
						self.IrcListen(line)
			self.c_print("%sStopped successful" % COLOR['red'] )
		except Exception, e:
			try: self.c_print("%sError on script :/ - %s" % ( COLOR['red'], e ) )
			except: self.c_print("%sError on script :/" % ( COLOR['red'] ) )
			if self.running: self.reconnect()
	
	def IrcListen(self, data):
		try: event = data.split(' ')[1]
		except: event = None
		
		if data.split(' ')[0] == 'PING':
			self.send('PONG %s :TIMEOUTCHECK' % self.server)
			#Maintenance 1h 30m
			if ( int( time.time() ) - self.assets['config']['assets_update'] ) >= 5400:
				self.UpdateAssets()
				if len( self.cleverbot['users'] ) > 0:
					tmp = self.cleverbot['users']
					for x in list( tmp ):
						if ( int( time.time() ) - self.cleverbot['users'][ x ]['last_use'] ) >= 120:
							del self.cleverbot['users'][ x ]
				
				#Clear stats
				_range = self.assets['config']['wordstats']['clean_range']
				if int( time.time() ) - self.assets['config']['wordstats']['last_clean'] >= _range:
					self.assets['config']['wordstats']['last_clean'] = int( time.time() )
					
					for user in list( self.assets['stats']['users'] ):
						if int( time.time() ) - self.assets['stats']['users'][ user ]['seen'] > _range:
							self.assets['stats']['users'].pop( user )
							
					for chan in list( self.assets['stats']['channels'] ):
						if int( time.time() ) - self.assets['stats']['channels'][ chan ]['seen'] > _range:
							self.assets['stats']['channels'].pop( chan )
							
					for word in list( self.assets['stats']['words'] ):
						if int( time.time() ) - self.assets['stats']['words'][ word ]['time'] > _range or self.assets['stats']['words'][ word ]['uses'] <= 5:
							self.assets['stats']['words'].pop( word )
							
					for link in list( self.assets['stats']['links'] ):
						if int( time.time() ) - self.assets['stats']['links'][ link ]['time'] > _range or self.assets['stats']['links'][ link ]['uses'] <= 3:
							self.assets['stats']['links'].pop( link )
							
				gc.collect()
		if event == '001':
			self.netname = util.getNetName(data)
			for chan in self.channels:
				self.Join( chan )
			self.c_print("%s[+] Channel Join Complete" % COLOR['yellow'])
			self.send('PRIVMSG NickServ IDENTIFY %s' % self.password )
			self.send('MODE %s +B' % self.nick)
			util.AutoMessages(self, False)
		if event == '433':
			newnick = ("%s_") % self.nick
			self.send('NICK %s' % newnick)
			self.nick = newnick
		if event in self.assets['config']['listen_events']:
			user = util.GetNick( data )
			chan = util.GetChannel( data )
			
			if event == 'JOIN':
				if user != self.nick:
					self.c_print( "%s%-s has joined %s" % ( COLOR['green'], user, chan ) )
					if self.names.get(chan): self.names[chan].setdefault(user, { "level": 0 })
					else: self.names.setdefault( chan, { user: { "level": 0 } } )
					if self.idle['chan'].get(chan): self.idle['chan'][chan] = int( time.time() )
					self._doJoin(chan, user)
				else:
					self.idle['chan'].setdefault(chan, int( time.time() ))
					self.names.setdefault( chan, { self.nick: { "level": 0 } } )
					self.send("NAMES :%s" % chan)
			if event == 'PART':
				self.c_print( "%s%-s has left %s" % ( COLOR['green'], user, chan ) )
				if user == self.nick:
					if self.names.get( chan ): self.names.pop( chan )
					if self.idle['chan'].get(chan): self.idle['chan'].pop( chan )
					if self.flood.get( chan ): self.flood.pop( chan )
				else:
					if self.names.get(chan):
						if self.names[chan].get(user):
							self.names[chan].pop(user)
					if self.idle['chan'].get(chan): self.idle['chan'][chan] = int( time.time() )
					self._doPart(chan, user)
			if event == 'NICK':
				newnick = data.split(" ")[2]
				self.c_print("%s%-s is now known as %s" % ( COLOR['green'], user, newnick ) )
				self._doNick(user, newnick)
				if user == self.nick: self.nick = newnick
				tmp_ = self.names
				for chan in list(tmp_):
					for name in list(tmp_[chan]):
						if name == user:
							if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
							lvl = self.names[chan][user]['level']
							if self.names[chan].get(user): self.names[chan].pop(user)
							self.names[chan].setdefault(newnick, { "level": lvl })
			if event == 'KICK':
				chan = data.split(" ")[2]
				kicked = data.split(" ")[3]
				self.c_print("%s[%s] %s was kicked by %s" % ( COLOR['green'], chan, kicked, user ) )
				self._doKick(chan, kicked)
				if kicked == self.nick: self.Join( chan )
				if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
				if self.names[chan].get(user): self.names[chan].pop(user)
			if event == 'MODE':
				chan = data.split(" ")[2]
				d = data.split(" ")
				modes = data[(len(d[0])+len(d[1])+len(d[2]))+3:]
				if chan != self.nick: self.c_print("%s[%s] %s sets mode: %s" % ( COLOR['green'], chan, user, modes ))
				if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
				self.send("NAMES :%s" % chan)
			if event == 'QUIT':
				self._doQuit(user)
				self.c_print( "%s%-s (Quit)" % ( COLOR['blue'], user ) )
				tmp_ = self.names
				for chan in list(tmp_):
					for name in list(tmp_[chan]):
						if name == user:
							if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
							if self.names[chan].get(user): self.names[chan].pop(user)
			if event == 'TOPIC':
				topic =	" ".join(data.split(':')[2:])
				self.c_print("%s[%s] %s changes topic to: %s" % ( COLOR['green'], chan, user, util.NoIrcColors( topic ) ))
				if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
			if event == '353':
				try:
					users = data.split(":")[2]
					if self.names.get( chan ) == None: self.names.setdefault( chan, {} )
					if self.names[chan].get( '@_tmpnames' ):
						self.names[chan]['@_tmpnames'].append( users )
					self.names[chan].setdefault( '@_tmpnames', [users] )
				except:
					pass
			if event == '366':
				if self.names.get( chan ) and self.names[chan].get( "@_tmpnames" ):
					_tmp_names = self.names[chan]["@_tmpnames"]
					self.names[ chan ] = { }
					for _lnames in _tmp_names:
						_lnames = _lnames.split(" ")
						for user in _lnames:
							level = util.GetLevel( user )
							if level <= 0: name = user
							else: name = user[1:]
							self.names[ chan ].setdefault( name, { "level": level } )
			if event == 'PRIVMSG' and chan:
				if self.idle['chan'].get(chan): self.idle['chan'][chan] = int(time.time())
				try:
					text = util.NoIrcColors( data[1:].split(':',1)[1] )
					action = util.GetMessageAction( text )
					if action: text = action
				except: pass
				
				#Word Stats
				if self.assets['config']['wordstats']['enable'] and user not in self.assets['config']['wordstats']['ignore'] and chan not in self.assets['config']['wordstats']['ignore']:
					util.WordStats( self.assets['stats'], user, chan, text, self.assets['config']['wordstats']['emoticonos'] )				
					
				cmd = text.split(' ')[0]
				try: prefix = cmd[0]
				except: prefix = ""
				tmp_text = text[len(cmd)+1:]
				thr_cmd = None
				cmd_info = self.assets['commands'].get( cmd[1:].lower() )
				if cmd_info == None:
					is_alias = util.isCmdAlias( self, cmd[1:].lower() )
					
					if self.assets['config']['single_channel'].get(chan) and self.assets['config']['single_channel'][chan].get( 'custom_command' ) and self.assets['config']['single_channel'][chan]['custom_command'].get( cmd[1:].lower() ):
						missing = { 'ignore': [], 'mod': False, 'alias': [] }
						cmd_info = dict( self.assets['config']['single_channel'][chan]['custom_command'][cmd[1:].lower()].items() + missing.items())
					
					if is_alias:
						cmd_info = self.assets['commands'][ is_alias ]
						cmd = "%s%s" % (prefix, is_alias)
				
				if cmd_info and chan not in cmd_info['ignore']:
					if self.limiter['commands'].get( chan ):
						if cmd[1:].lower() in self.limiter['commands'][ chan ]:
							cmd_info = None
				
				if cmd_info and cmd_info['active'] and chan not in cmd_info['ignore'] and chan not in self.assets['config']['flood_protection']['ignore'] and self.assets['config']['flood_protection']['enable']:
					if self.flood.get( chan ):
						_flood = self.flood[ chan ]
						_fltxt = cmd[1:].lower() if self.assets['config']['flood_protection']['only_cmd'] else text.lower()
						_config = self.assets['config']['flood_protection']
						def _updatefl():
							_flood['time'] = int( time.time() )
							if _flood['text'] == _fltxt: _flood['count'] +=1
							else: _flood['count'] = 1
							_flood['text'] = _fltxt
							
						if _flood['pass'] and (int( time.time() ) - _flood['time']) >= _config['block_time']:
							_flood['count'] = 1
							_flood['pass'] = False
						elif _flood['pass']:
							_updatefl()
							cmd_info = None
						else:
							if _flood['count'] >= _config['max_reps'] and _flood['text'] == _fltxt and (int( time.time() ) - _flood['time']) >= _config['min_time'] and (int( time.time() ) - _flood['time']) <= _config['max_time']:
								if _flood['pass']:
									_updatefl()
									cmd_info = None
								else:
									self.message( "13> 4Flooding with 14({reps} \"{txt}\" on {time}secs)4 blocking all commands on1 {chan} 14({timebl}secs)".format(chan = chan, reps = _flood['count'], txt = _fltxt, time = (int( time.time() ) - _flood['time']), timebl = _config['block_time']), chan )
									_flood['pass'] = True
									cmd_info = None
									_updatefl()
							else:
								_updatefl()
					else:
						self.flood.setdefault( chan, { 'time': int( time.time() ), 'count': 1, 'text': cmd[1:].lower(), 'pass': False } )
				
				if user in self.assets['config']['mods']:
					self.c_print("%s[%s] %s%-s: %s%-s" % (COLOR['green'], chan, COLOR['cyan'], user, COLOR['white'], text))
					if self.assets['config']['prefix'] == prefix and cmd_info:
						if cmd_info['active'] and chan not in cmd_info['ignore']:
							thr_cmd = threading.Thread(target=onModCommand, args=(self, chan, user, cmd[1:].lower(), tmp_text,))
				else:
					self.c_print("%s[%s] %s%-s: %s%-s" % (COLOR['green'], chan, COLOR['magenta'], user, COLOR['white'], text))
					if self.assets['config']['prefix'] == prefix and cmd_info:
						if cmd_info['active'] and chan not in cmd_info['ignore']:
							thr_cmd = threading.Thread(target=onCommand, args=(self, chan, user, cmd[1:].lower(), tmp_text,))
				if thr_cmd:
					thr_cmd.setDaemon(True)
					thr_cmd.start()
	
	def quit(self, rq = "Shutdown"):
		self.UpdateAssets()
		self.send("QUIT %s" % rq)
		self.c_print("%s%-s" % ( COLOR['red'], "Quit: %s" % rq ) )
	
	def reconnect(self):
		if self.running:
			try:
				self.UpdateAssets()
				try: self.irc.shutdown(1)
				except: pass
				time.sleep(25)
				self.start()
			except Exception, e:
				print e
				self.c_print( "%s[-] Can't connect, trying again..." % ( COLOR['red'] ) )
				time.sleep(30)
				self.reconnect()
	
	def c_print( self, msg ):
		msg = util.NoIrcColors( msg )
		msg = u"[%s] [%s] %s\r\n" % (self.netname, self.nick, msg)
		try: sys.stdout.write( msg )
		except: sys.stdout.write( msg.encode("UTF-8") )
		sys.stdout.write( Style.RESET_ALL )
	
	#Editable
	def _doJoin(self, chan, user):
		if self.assets['config']['single_channel'].get(chan):
			if self.assets['config']['single_channel'][chan].get("welcome_msg"):
				try: self.message(self.assets['config']['single_channel'][chan]['welcome_msg'].format(user = user, chan = chan, color = "\u0003", underline = "\u001f", bold = "\u0002", italic = "\u001d"), chan)
				except: self.message(self.assets['config']['single_channel'][chan]['welcome_msg'], chan)
	def _doPart(self, chan, user):
		return
	def _doQuit(self, user, reason = ""):
		return
	def _doKick(self, chan, user, reason = ""):
		return
	def _doNick(self, user, newuser):
		return
	
	def Join(self, chan):
		self.send("JOIN %s" % chan)
	def Part(self, chan):
		self.send("PART %s" % chan)
	
	def message(self, msg, chan, show = True, type = "m"):
		current = int( time.time() )
		time_passed = (current - self.limiter['messages']['last_check'])
		self.limiter['messages']['last_check'] = current
		self.limiter['messages']['allowance'] += time_passed * (self.limiter['messages']['rate'] / self.limiter['messages']['per'])
		if self.limiter['messages']['allowance'] > self.limiter['messages']['rate']:
			self.limiter['messages']['allowance'] = self.limiter['messages']['rate']
		if self.limiter['messages']['allowance'] < 1: 
			timer = threading.Timer(1.5, self.message, [msg, chan,  show, type])
			timer.start()
		else:
			self.limiter['messages']['allowance'] -= 1
			if self.assets['config'].get('nocolors'): msg = util.NoIrcColors( msg )
			if show == True: self.c_print( "%s[%s] %s%-s: %s%-s" % (COLOR['green'], chan, COLOR['yellow'], self.nick, COLOR['white'], msg[:450]) )
			
			if type == "n": self.send( "NOTICE %s :%s" % ( chan, msg[:450]) )
			elif type == "a": self.send( "PRIVMSG %s :\001ACTION %s\001" % ( chan, msg[:450]) )
			else: self.send( "PRIVMSG %s :%s" % ( chan, msg[:450]) )
			
			if len(msg) > 450:
				self.message( msg[450:], chan,  show, type)
	
	def send( self, msg ):
		msg = u"%s\r\n" % msg
		try: self.irc.send(msg.encode('utf-8'))
		except Exception, e: pass
	
	def LoadAssets(self):
		self.assets = dict(
			config = json.loads( open( "%s/config.json" % self.path ).read() ),
			commands = json.loads( open( "%s/commands.json" % self.path ).read() ),
			stats = json.loads( open( "%s/stats.json" % self.path ).read() ),
			quotes = json.loads( open( "%s/quote.json" % self.path ).read() ),
			aways = json.loads( open( "%s/aways.json" % self.path ).read() ),
			api = json.loads( open( "%s/api.json" % self.path ).read() )
		)
		
	def UpdateAssets(self):
		self.assets['config']['assets_update'] = int( time.time() )
		Assets = dict(
			config = { "file": "%s/config.json" % self.path, "var": self.assets['config'] },
			stats = { "file": "%s/stats.json" % self.path, "var": self.assets['stats'] },
			quotes = { "file": "%s/quote.json" % self.path, "var": self.assets['quotes'] },
			aways = { "file": "%s/aways.json" % self.path, "var": self.assets['aways'] },
			commands = { "file": "%s/commands.json" % self.path, "var": self.assets['commands'] }
		)
		for x in Assets:
			try:
				with open( Assets[ x ]['file'], "r+") as jsonFile:
					data = json.load( jsonFile )
					jsonFile.seek( 0 )
					jsonFile.write( json.dumps( Assets[ x ]['var'], sort_keys=True, indent=4 ) )
					jsonFile.truncate()
			except:
				pass
			jsonFile = None
