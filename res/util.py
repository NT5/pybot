#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-
import re, platform, urllib2, urllib, json, time, random, threading
from HTMLParser import HTMLParser

def getinfo(): return platform.uname()

def EmoticonCount( text, string = "" ):
	text = text.lower()
	regex = re.compile("%s(?:\d{1,2}(?:,\d{1,2})?)?" % string, re.UNICODE)
	return len( regex.findall( text ) )
	
def WordStats( src, user, chan, text, emoticons = ""):
	_default = { "letters": 0, "words": 0, "lines": 0, "smiles": 0, "seen": 0, "quote": "", "timeline": { "ap": 0, "date": [] } }
	if src['users'].get( user ) == None:
		src['users'].setdefault( user, _default )
	if src['channels'].get( chan ) == None:
		src['channels'].setdefault( chan, _default )
	
	_smiles = EmoticonCount( text, emoticons )
	_letters = len( text.replace( " ", "" ) )
	_words = len( text.split( " " ) )
	_lines = 1
	
	def _setdata( u ):
		u['smiles'] += _smiles
		u['letters'] += _letters
		u['words'] += _words
		u['lines'] += _lines
		
		_ap =  ( _smiles*10+_letters*3+_words*5+_lines*2 ) * (2 if int( time.time() ) - u['seen'] <= 60 else 1)
		
		u['timeline']['ap'] += _ap
		if len( u['timeline']['date'] ) <= 0: u['timeline']['date'].append( { "time": int( time.time() ), "ap": u['timeline']['ap'] } )
		else:
			_id = ( len(u['timeline']['date'])-1 )
			if int( time.time() ) - u['timeline']['date'][_id]['time'] <= 86400:
				u['timeline']['date'][_id]['ap'] = u['timeline']['ap']
			else:
				u['timeline']['date'].append( { "time": int( time.time() ), "ap": u['timeline']['ap'] } )
		if len( u['timeline']['date'] ) >= 16: u['timeline']['date'].pop(0)
			
		u['seen'] = int( time.time() )
		u['quote'] = text[:50]
		
	_setdata( src['users'][ user ] )
	_setdata( src['channels'][ chan ] )
	
	_urls = getURLS( text )
	if len( _urls ) > 0:
		for url in _urls:
			if src['links'].get( url ):
				src['links'][ url ]['uses'] += 1
				src['links'][ url ]['user'] = user
				src['links'][ url ]['time'] = int( time.time() )
			else:
				src['links'].setdefault( url, { 'uses': 1, 'user': user, 'time': int( time.time() ) } )
				
	_text = removeall( text, [ ".", ",",";", "_", "-", "/", "\\", "?", "!", "&", "$", "{", "}", "[", "]", "*", "+", "(", ")", ":", "<", ">", "@", "=", "\"", "'", "%", "#", "~", "^" ], True, " " )
	if _text:
		_worddict = _text.split( " " )
		for word in _worddict:
			if len( word ) >= 3 and isInt( word ) == False:
				if src['words'].get( word.lower() ):
					w = src['words'][ word.lower() ]
					w['uses'] += 1
					w['user'] = user
					w['time'] = int( time.time() )
				else:
					src['words'].setdefault( word.lower(), { 'uses': 1, 'user': user, 'time': int( time.time() ) } )
	
def _cmdLimiter( self, action, chan, cmd ):
	if action == 'b':
		if self.limiter['commands'].get( chan ):
			if cmd not in self.limiter['commands'][ chan ]:
				self.limiter['commands'][ chan ].append( cmd )
		else:
			self.limiter['commands'].setdefault( chan, [ cmd ] )
	else:
		if self.limiter['commands'].get( chan ) and cmd in self.limiter['commands'][ chan ]:
			if len( self.limiter['commands'][ chan ] ) == 1:
				self.limiter['commands'].pop( chan )
			else:
				self.limiter['commands'][ chan ].pop( self.limiter['commands'][ chan ].index( cmd ) )

def isCmdAlias(self, text):
	for cmd in self.assets['commands']:
		if text in self.assets['commands'][ cmd ]['alias']:
			return cmd
	return None
				
def AutoMessages(self, show = True):
	_count = 0
	for chan in self.assets['config']['single_channel']:
		if self.assets['config']['single_channel'][chan].get('auto_msgs'):
			if self.assets['config']['single_channel'][chan]['auto_msgs']['active']:
				_count = _count + 1
				if show and int( int( time.time() ) - self.idle['chan'][chan] ) <= 1800:
					self.message("10>14 %s" % random.choice(self.assets['config']['single_channel'][chan]['auto_msgs']['messages']), chan)
	timer = threading.Timer(900, AutoMessages, [self])
	if _count >= 1: timer.start()
	else: timer.cancel()
	
def GetLangStrings( self, strings, user, chan ):
	_uc_ES = self.assets['config']['use_langs'].get('es_ES')
	_uc_EN = self.assets['config']['use_langs'].get('en_US')
	if _uc_ES and user in _uc_ES:
		return strings["es_ES"].gettext
	elif _uc_EN and user in _uc_EN:
		return strings["en_US"].gettext
	elif _uc_ES and chan in _uc_ES:
		return strings["es_ES"].gettext
	elif _uc_EN and chan in _uc_EN:
		return strings["en_US"].gettext
	else:
		return strings["en_US"].gettext

def NoHTML( text ):
	parser = HTMLParser()
	return parser.unescape( text )

def NoIrcColors( text ):
	regex = re.compile("\x1d|\x0f|\x1f|\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
	return regex.sub('', text)
	
def NoMCColors( text ):
	regex = re.compile("\xA7(?:[a-zA-Z]|[0-9])?", re.UNICODE)
	return regex.sub('', text)
	
def removeall( text, rem, non_ascii = False, re_char = '' ):
	if non_ascii: text = text.encode("ascii", "ignore")
	for char in rem:
		text = text.replace( char, re_char )
	return text if len( text ) > 0 else None
	
def GetMessageAction( text ):
	regex = re.compile("\001ACTION (.+)\001(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
	try:
		return regex.findall(text)[0]
	except:
		return None

def getNetName( text ):
	regex = re.compile("(?:Welcome|Bienvenido) (?:to the|to|a) ([-.!@$#%^&*()<>|_+=\;:,?[{\]}\w]*)", re.UNICODE)
	try: return regex.findall(text)[0]
	except: return None

def getOsuLink( text, type = "b" ):
	if type == "b": _formated = "(?:http|https)://osu.ppy.sh/(b|s)+/(\d+)?"
	elif type == "u": _formated = "(?:http|https)://osu.ppy.sh/u/(\d+)?"
	else: _formated = ""
	regex = re.compile("%s" % _formated, re.UNICODE)
	r = regex.search(text)
	if r:
		return r.groups()
	else:
		return None
	
def getURLS( text ):
	regex = re.compile( "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.UNICODE )
	return regex.findall( text )

def GetLevel( data ):
	level = data[:1]
	if level == "~" or level == "q": return 5
	elif level == "&" or level == "a": return 4
	elif level == "@" or level == "o": return 3
	elif level == "%" or level == "h": return 2
	elif level == "+" or level == "v": return 1
	else: return 0
		
def GetChannel(data):
	try:
		channel = data.split('#')[1]
		channel = channel.split(':')[0]
		channel = '#' + channel
		channel = channel.strip(' \t\n\r')
		return channel
	except:
		return None
		
def GetNick(data):
	try:
		nick = data.split('!')[0]
		nick = nick.replace(':', ' ')
		nick = nick.replace(' ', '')
		nick = nick.strip(' \t\n\r')
		return nick
	except:
		return None
		
def gettext( text, index, tock = " " ):
	try:
		return text.split( tock )[ index ]
	except:
		return None
		
def neighborhood(iterable):
	iterator = iter(iterable)
	prev = None
	item = iterator.next()
	for next in iterator:
		yield (prev,item,next)
		prev = item
		item = next
	yield (prev,item,None)

def getDHMS(seconds):
	days = seconds / 86400
	seconds -= 86400 * days
	hours = seconds / 3600
	seconds -= 3600 * hours
	minutes = seconds / 60
	seconds -= 60 * minutes
	messages = []
	if days > 0: messages.append( "%ddays" % days )
	if hours > 0: messages.append( "%2dhrs" % hours )
	if minutes > 0: messages.append( "%2dmin" % minutes )
	if seconds > 0: messages.append( "%2dsecs" % seconds )
	if len( messages ) > 0:
		return ", ".join( messages )
	else:
		return "%2dsecs" % seconds

def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))
	
def json_request( url, headers, met = None ):
	req = urllib2.Request(url, met, headers)
	json = urllib2.urlopen(req, timeout = 35).read()
	(true,false,null) = (str( True ),str( False ),str( None ))
	return eval(json)
	
def web_request( url, headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' } ):
	req = urllib2.Request(url, None, headers)
	query = urllib2.urlopen( req, timeout = 35 )
	response = query.read()
	query.close()
	return response

def get_google_translate(text, translate_lang, source_lang=None):
	if source_lang == None: source_lang= 'auto' 
	params = urllib.urlencode({'client':'t', 'tl':translate_lang, 'q':text.encode('utf-8'), 'sl':source_lang})
	http_headers = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5;Windows NT)"} 
	request_object = urllib2.Request('http://translate.google.com/translate_a/t?'+params, None, http_headers)
	try: 
		response = urllib2.urlopen(request_object, timeout = 15)
		string = re.sub(',,,|,,',',"0",', response.read()) 
		n = json.loads(string) 
		translate_text = n[0][0][0] 
		res_source_lang = n[2] 
		return True, res_source_lang, translate_text 
	except Exception, e:
		return False, '', e
		
def get_google_search( text, max = 3 ):
	def parse_html( string ):
		string = removeall( string, rem = [ "<b>", "</b>" ], re_char = "" )
		return NoHTML( string.replace("<br>", '').decode("UTF-8") )
	def regx( string ):
		regex = re.compile("<a class=\"l\" href=\"(.*?)\".*?\">(.*?)</a></h2>.*?<span class=\"s\">(.*?)</span><br>",re.UNICODE)
		return regex.findall(string)
		
	data = web_request( "http://www.google.com/custom?hl=en&client=pub-4099951843714863&q=%s" % ( urllib2.quote(text.encode('utf-8')) ), headers = {  'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36' } )
	
	q = regx( data[3000:-8000] )
	_res = []
	_count = 0
	for res in q:
		_count += 1
		if _count <= max:
			_res.append( { 'title': parse_html( res[1] ), 'link': parse_html(res[0]), 'description': parse_html(res[2]) } )
	return _res

def uniq(input):
	output = []
	for x in input:
		if x not in output:
			output.append(x)
	return output

def gettext( text, index, tock = " " ):
	try:
		return text.split( tock )[ index ]
	except:
		return None
	
def isInt(a):
	try:
		int(a)
		return True
	except:
		return False

