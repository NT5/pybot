#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-
import re, platform, urllib2, json, time
from HTMLParser import HTMLParser

def getinfo(): return platform.uname()

def EmoticonCount( text, string = "" ):
	text = text.lower()
	regex = re.compile("%s(?:\d{1,2}(?:,\d{1,2})?)?" % string, re.UNICODE)
	return len( regex.findall( text ) )

def WordStats( user, text, emoticons = ""):
	smiles = ( user['smiles'] + EmoticonCount( text, emoticons ) )
	letters = ( len( text.replace( " ", "" ) ) + user['letters'] )
	words = ( len( text.split( " " ) ) + user['words'] )
	lines = ( user['lines'] + 1 )
	return { "letters": letters, "words": words, "lines": lines, "smiles": smiles, "seen": int( time.time() ), "quote": text[:50] }

def NoHTML( text ):
	parser = HTMLParser()
	return parser.unescape( text )

def NoIrcColors( text ):
	regex = re.compile("\x0f|\x1f|\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
	return regex.sub('', text)
	
def GetMessageAction( text ):
	regex = re.compile("\001ACTION (.+)\001(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
	try:
		return regex.findall(text)[0]
	except:
		return None

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
	json = urllib2.urlopen(req).read()
	(true,false,null) = (str( True ),str( False ),str( None ))
	return eval(json)
	
def web_request( url, headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' } ):
	req = urllib2.Request(url, None, headers)
	response = urllib2.urlopen( req )
	return response.read()

def parsemodes(string):
	# +ao-vh Shana Shana Eiko Eiko
	valid = ["q","a","o","h","v"]
	levels = []
	names = []
	for level in string.split(" ")[0]:
		levels.append( GetLevel(level) )

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