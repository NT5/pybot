#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import urllib2, json, time

class NpLastFM:
	def __init__(self, api_key, user, sender):
		self.sender = sender
		self.key = api_key
		self.user = user
		self.artist = None
		self.name = None
		self.url = { "base": "http://ws.audioscrobbler.com", "req": "/2.0/?method=user.getrecenttracks&limit=1&user={user}&api_key={key}&format=json".format( user = self.user, key = self.key ) }
		
	def request(self):
		url = "{base}{req}".format( base = self.url['base'], req = self.url['req'] )
		q = urllib2.urlopen( urllib2.Request(url, None, {}) ).read()
		(true, false, null) = ( str( True ), str( False ), str( None ) )
		return eval( q )
		
	def analyze(self):
		try:
			q = self.request()
			if type(q['recenttracks']['track']) == type([]): q = q['recenttracks']['track'][0]
			else: q = q['recenttracks']['track']
			
			if q.get('@attr') and q['@attr'].get('nowplaying') and q['name'] != self.name:
				self.artist = q['artist']['#text']
				self.name = q['name']
				return { "name": q['name'].decode("unicode-escape"), "artist": q['artist']['#text'].decode("unicode-escape") }
			else:
				return None
		except Exception, e: return None
	
	def run(self):
		print "[+] [%s] LastFM Now playing started" % self.user
		while True:
			#Editable
			_make_q = False
			for loc in self.sender:
				for chan in loc.assets['config']['last_fm']:
					if loc.idle['chan'].get(chan):
						if int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
							_make_q = True
							break
						
			#If make request
			if _make_q:
				data = self.analyze()
				if data:
					#Send messages to bots
					for loc in self.sender:
						for chan in loc.assets['config']['last_fm']:
							if loc.idle['chan'].get(chan):
								if int( int( time.time() ) - loc.idle['chan'][chan] ) <= 1800:
									loc.message( "13[0,4LastFM13]1 13[10%s13]14 %s - %s" % ( self.user, data['name'], data['artist'] ), chan, False )
			#Delay
			time.sleep(25)

