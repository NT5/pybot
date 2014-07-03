#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import urllib2, json, time

class NpLastFM:
	def __init__(self, api_key, sender):
		self.sender = sender
		self.key = api_key
		self.users = {}
		self.running = True
		self.limiter = { 'rate': 1500, 'per': (5 * 60) }
		self.allowance = self.limiter['rate']
		self.last_check = int( time.time() )
		self.url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&user={user}&api_key={key}&format=json"
		
	def request(self, users):
		data = {}
		(true, false, null) = ( str( True ), str( False ), str( None ) )
		for user in users:
			try:
				current = int( time.time() )
				time_passed = (current - self.last_check)
				self.last_check = current
				self.allowance += time_passed * (self.limiter['rate'] / self.limiter['per'])
				if self.allowance > self.limiter['rate']:
					self.allowance = self.limiter['rate']
				if self.allowance < 1:
					print "[-] LastFM rate limit exceeded"
					self.allowance = self.limiter['rate']
					time.sleep(60)
				else:
					url = self.url.format( user = user, key = self.key )
					data.setdefault( user, eval( urllib2.urlopen( urllib2.Request(url, None, {}) ).read() ) )
					self.allowance -= 1
					time.sleep(1)
			except: pass
		return data
		
	def analyze(self, data):
		_data = {}
		for user in data:
			try:
				q = data[ user ]
				if type(q['recenttracks']['track']) == type([]): q = q['recenttracks']['track'][0]
				else: q = q['recenttracks']['track']
				
				if q.get('@attr') and q['@attr'].get('nowplaying'):
					if self.users.get( user ):
						if q['name'] != self.users[user]['name']:
							_data.setdefault( user, { "name": q['name'].decode("unicode-escape"), "artist": q['artist']['#text'].decode("unicode-escape") } )
						
						self.users[ user ] = { 'artist': q['artist']['#text'], 'name': q['name'], 'date': int( time.time() ) }
					else:
						self.users.setdefault(user, { 'artist': q['artist']['#text'], 'name': q['name'], 'date': int( time.time() ) } )
						_data.setdefault( user, { "name": q['name'].decode("unicode-escape"), "artist": q['artist']['#text'].decode("unicode-escape") } )
			except: pass
		return _data
	
	def run(self):
		print "[+] LastFM Now playing started"
		while self.running:
			_users = []
			for loc in self.sender:
				for user in loc.assets['config']['last_fm']:
					for chan in loc.assets['config']['last_fm'][user]:
						if loc.idle['chan'].get(chan) and int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
								if user not in _users: _users.append( user )
			
			for x in list(self.users):
				if int( time.time() ) - self.users[x]['date'] >= 1800: self.users.pop(x)
				
			if len( _users ) > 0:
				data = self.analyze( self.request( _users ) )
				if len( data ) > 0:
					for loc in self.sender:
						for user in loc.assets['config']['last_fm']:
							if data.get(user):
								for chan in loc.assets['config']['last_fm'][user]:
									if loc.idle['chan'].get(chan) and int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
										loc.message( "13[0,4LastFM13]1 13[10%s13]14 %s - %s" % ( user, data[user]['name'], data[user]['artist'] ), chan, False )
			#Delay
			time.sleep(35)
			
	def stop( self ):
		self.running = False
		print "[-] LastFM Now playing stopped"

