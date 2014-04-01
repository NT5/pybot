#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import gettext
import util as util, sys, time, random, urllib2, re
from google.search import GoogleSearch, SearchError
from vcmpQuery import vcmpQuery

from encryp import Encryp
cryp = Encryp()

#Translation directory and file
DIR = "locale"
APP = "commands"
gettext.textdomain(APP)
gettext.bindtextdomain(APP, DIR)

#Available languages
LANG = ["es_ES","en_US"]
strings = {}

for lang in LANG:
	strings.setdefault(lang, gettext.translation(APP, DIR, languages=[lang], fallback = True))
	strings[lang].install()

	
def onModCommand(self, chan, user, cmd, text):
	if self.assets['config']['use_langs'].get('es_ES') and user in self.assets['config']['use_langs']['es_ES']:
		_ = strings["es_ES"].gettext
	else:
		_ = strings["en_US"].gettext
	
	prx = self.assets['config']['prefix']
	if cmd == 'exe':
		if len(text) > 0:
			try: exec text
			except Exception, e:
				self.message( _('4Error:1 %s') % str( e ), chan )		
		else:
			self.message( _("%s%s <string code>") % (prx, cmd), chan)
			
	elif cmd == 'adduser':
		if len(text) > 0:
			text2 = text.split(' ')[0]
			if text2 in self.assets['config']['mods']:
				self.message(_("10>1 %s already in bot list.") % text2, chan)
			else:
				self.assets['config']['mods'].append( text2 )
				self.message(_("10>1 %s is now bot user.") % text2, chan)
		else:
			self.message(_("7Syntax:1 %s%s <user>, Current Users: %s") % (prx, cmd, ", ".join(self.assets['config']['mods'])), chan)
	
	elif cmd == 'deluser':
		if len(text) > 0:
			exclude = text.split(' ')[0]
			if exclude in self.assets['config']['mods']:
				tmp = self.assets['config']['mods']
				self.assets['config']['mods'] = []
				for x in list(tmp):
					if x != exclude: self.assets['config']['mods'].append( x )
				self.message(_("10>1 %s is not more bot user.") % exclude, chan)
			else:
				self.message(_("10>1 %s unknown name, Current Users: %s") % (exclude, ", ".join(self.assets['config']['mods'])), chan)
		else:
			self.message(_("7Syntax:1 %s%s <user>, Current Users: %s") % (prx, cmd, ", ".join(self.assets['config']['mods'])), chan)
	
	elif cmd == 'control':
		if len(text) > 0:
			place = util.gettext( text, 0 )
			param = util.gettext( text, 1 )
			value = util.gettext( text, 2 )
			if place == 'stats':
				if param == 'del':
					if value:
						if self.assets['stats'].get( value ):
							self.message( _("> %s 4is now delete from user stats.") % value, chan )
							self.assets['stats'].pop( value )
						else:
							self.message( _("> %s 4is unknown name to me") % value, chan )
					else:
						self.message(_('7Syntax:1 %s%s %s %s <user>') % ( prx, cmd, place, param ), chan )
				elif param == 'clean':
					users = []
					tmp = self.assets['stats']
					for x in tmp:
						if ( int ( int( time.time() ) - int( self.assets['stats'][ x ]['seen'] ) ) ) >= int( self.assets['config']['user_stats']['clean_range'] ):
							users.append( x )
					if len( users ) > 0:
						for x in users:
							self.assets['stats'].pop( x )
						self.message( _("11>1 %i 4users cleaned from users stats 1(%s)4, in a range12 %s") % ( len( users ), ", ".join(users), util.getDHMS( self.assets['config']['user_stats']['clean_range'] ) ), chan )
					else:
						self.message( _("11>4 No users found in range (%s)") % util.getDHMS( self.assets['config']['user_stats']['clean_range'] ), chan )
				elif param == 'ignore':
					if value:
						if value in self.assets['config']['user_stats']['ignore']:
							tmp = self.assets['config']['user_stats']['ignore']
							self.assets['config']['user_stats']['ignore'] = []
							for x in tmp:
								if x != value:
									self.assets['config']['user_stats']['ignore'].append( x )
							self.message(_("> %s 4is not more in ignore list") % value, chan)
						else:
							if value in self.names[ chan ]:
								self.assets['config']['user_stats']['ignore'].append( value )
								self.message( _("> %s 4are now in ignore list") % value, chan )
							else:
								self.message( _("> %s 4is not on1 %s") % ( value, chan ), chan )
					else:
						self.message(_('7Syntax:1 %s%s %s %s <user>') % ( prx, cmd, place, param ), chan )
				else:
					self.message(_('7Syntax:1 %s%s %s <del/clean/ignore>') % ( prx, cmd, place ), chan )
			elif place == 'osu':
				val_param = util.gettext( text, 3 )
				par_value = util.gettext( text, 4 )
				if param == 'request':
					if value == 'set':
						if val_param:
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get("osu_req"):
									if val_param in self.assets['config']['single_channel'][chan]["osu_req"]['users']:
										self.message(_("10>1 \"%s\" 4is already on the list of this channel") % val_param, chan)
									else:
										self.assets['config']['single_channel'][chan]["osu_req"]['users'].append(val_param)
								else:
									self.assets['config']['single_channel'][chan].setdefault( "osu_req", { "active": True, "users": [val_param] } )
							else:
								self.assets['config']['single_channel'].setdefault( chan, { "osu_req": { "active": True, "users": [val_param] } } )
							self.message( _("10> 14Osu request set to1 %s 14and send to13:1 %s on BanchoNet") % ( chan, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users']) ), chan )
						else:
							self.message(_('7Syntax:1 %s%s %s %s <user>') % ( prx, cmd, place, param ), chan )
					elif value == 'del':
						if val_param:
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get("osu_req"):
									if val_param in self.assets['config']['single_channel'][chan]['osu_req']['users']:
										if len(self.assets['config']['single_channel'][chan]['osu_req']['users']) > 1:
											id = self.assets['config']['single_channel'][chan]['osu_req']['users'].index(val_param)
											self.assets['config']['single_channel'][chan]['osu_req']['users'].pop(id)
											self.message(_("10>1 \"%s\" 4deleting channel from1 %s") % (val_param, chan), chan)
										else:
											self.assets['config']['single_channel'][chan].pop('osu_req')
											self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (val_param, chan), chan)
									else:
										self.message( _("> %s 4is unknown name to me") % val_param, chan )
								else:
									self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
							else:
								self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
						else:
							self.message(_('7Syntax:1 %s%s %s %s <user>') % ( prx, cmd, place, param ), chan )
					elif value == 'remove':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								_users = self.assets['config']['single_channel'][chan]['osu_req']['users']
								self.assets['config']['single_channel'][chan].pop('osu_req')
								self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (", ".join(_users), chan), chan)
							else:
								self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
					elif value == 'turn':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								_Ac = self.assets['config']['single_channel'][chan]['osu_req']['active']
								if _Ac == True: self.assets['config']['single_channel'][chan]['osu_req']['active'] = False
								else: self.assets['config']['single_channel'][chan]['osu_req']['active'] = True
								self.message(_("10>14 Osu!request are now turned %s, in1 %s") % ( _("off") if _Ac == True else _("on"), chan ), chan)
							else:
								self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
					elif value == 'get':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								self.message(_("10> 13Osu!request14 on1 %s 14are send to1 %s") % ( chan, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users'])), chan)
							else:
								self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is unknown channel to me") % chan, chan )
					else:
						self.message(_('7Syntax:1 %s%s %s <set/del/remove/turn/get>') % ( prx, cmd, place ), chan )
				elif (param == 'bancho') | (param == 'np'):
					if param == 'bancho': _sec = 'bancho_listen'
					else: _sec = 'osu_np'
					if value:
						if value == 'set':
							if val_param:
								if par_value and str(par_value)[0] == "#":
									if self.assets['config'][_sec].get(val_param):
										if par_value in self.assets['config'][_sec][val_param]:
											self.message(_("10>1 \"%s\" 4is already on the list of this user") % par_value, chan)
										else:
											self.assets['config'][_sec][val_param].append(par_value)
									else:
										self.assets['config'][_sec].setdefault(val_param, [par_value])
										if param == 'np':
											self.notice("> %s Post KEY: %s" % (val_param, cryp.encode(val_param)), user)
									self.message( _("10> 14Messages of1 %s 14are now send to13:1 %s") % ( val_param, ", ".join(self.assets['config'][_sec][val_param]) ), chan )
								else:
									self.message(_('7Syntax:1 %s%s %s %s %s %s <#channel>') % ( prx, cmd, place, param, value, val_param ), chan )
							else:
								self.message(_('7Syntax:1 %s%s %s %s %s <user>') % ( prx, cmd, place, param, value ), chan )
						elif value == 'del':
							if val_param:
								if par_value and str(par_value)[0] == "#":
									if self.assets['config'][_sec].get(val_param):
										if par_value in self.assets['config'][_sec][val_param]:
											if len(self.assets['config'][_sec][val_param]) > 1:
												id = self.assets['config'][_sec][val_param].index(par_value)
												self.assets['config'][_sec][val_param].pop(id)
												self.message(_("10>1 \"%s\" 4deleting channel from1 %s") % (par_value, val_param), chan)
											else:
												self.assets['config'][_sec].pop( val_param )
												self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (val_param, _sec), chan)
										else:
											self.message( _("10>1 %s 4is unknown channel to me") % par_value, chan )
									else:
										self.message( _("> %s 4is unknown name to me") % val_param, chan )
								else:
									self.message(_('7Syntax:1 %s%s %s %s %s %s <#channel>') % ( prx, cmd, place, param, value, val_param ), chan )
							else:
								self.message(_('7Syntax:1 %s%s %s %s %s <user>') % ( prx, cmd, place, param, value ), chan )
						elif value == 'remove':
							if val_param:
								if self.assets['config'][_sec].get(val_param) != None:
									self.assets['config'][_sec].pop( val_param )
									self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (val_param, _sec), chan)
								else:
									self.message( _("> %s 4is unknown name to me") % val_param, chan )
							else:
								self.message(_('7Syntax:1 %s%s %s %s %s <user>') % ( prx, cmd, place, param, value ), chan )
						elif value == 'get':
							if val_param:
								if self.assets['config'][_sec].get(val_param) != None:
									self.message( _("10> 14Messages of1 %s 14are send to13:1 %s") % ( val_param, ", ".join(self.assets['config'][_sec][val_param]) ), chan )
									if param == 'np':
										self.notice("> %s Post KEY: %s" % (val_param, cryp.encode(val_param)), user)
								else:
									self.message( _("> %s 4is unknown name to me") % val_param, chan )
							else:
								self.message(_('10> 14All users of1 \"%s\"13:1 %s') % ( _sec, ", ".join(self.assets['config'][_sec]) ), chan )
						else:
							self.message(_('7Syntax:1 %s%s %s %s <set/del/remove/get>') % ( prx, cmd, place, param ), chan )
					else:
						self.message(_('7Syntax:1 %s%s %s %s <set/del/remove/get>') % ( prx, cmd, place, param ), chan )
				else:
					self.message(_('7Syntax:1 %s%s %s <bancho/np/request>') % ( prx, cmd, place ), chan )
			elif place == 'commands':
				if param == 'turn':
					if value:
						if self.assets['commands'].get( value ):
							if value != cmd:
								if self.assets['commands'][ value ]['active'] == True:
									self.assets['commands'][ value ]['active'] = False
									self.message( _("> \"%s\" 4are now turn off for all channels") % value, chan )
								else:
									self.assets['commands'][ value ]['active'] = True
									self.message( _("> \"%s\" 4are now turn on for all channels") % value, chan )
							else:
								self.message(_(">4 This is not allowed."), chan)
						else:
							self.message( _("> %s 4is unknow command to me") % value, chan )
					else:
						self.message(_('7Syntax:1 %s%s %s %s <command>') % ( prx, cmd, place, param ), chan )
				elif param == 'ignore':
					if value:
						if value != cmd:
							if self.assets['commands'].get( value ):
								if chan not in self.assets['commands'][ value ]['ignore']:
									self.assets['commands'][ value ]['ignore'].append( chan )
									self.message( _("> \"%s\" 4are now ignore on1 %s") % ( value, chan ), chan )
								else:
									tmp = self.assets['commands'][ value ]['ignore']
									self.assets['commands'][ value ]['ignore'] = []
									for x in tmp:
										if x != chan:
											self.assets['commands'][ value ]['ignore'].append( x )
									self.message( _("> \"%s\" 4are now listened on1 %s") % ( value, chan ), chan )
							else:
								self.message( _("> %s 4is unknow command to me") % value, chan )
						else:
							self.message(_(">4 This is not allowed."), chan)
					else:
						self.message(_('7Syntax:1 %s%s %s %s <command>') % ( prx, cmd, place, param ), chan )
				elif param == 'formod':
					if value:
						if value != cmd:
							if self.assets['commands'].get( value ):
								if self.assets['commands'][ value ]['mod'] == True:
									self.assets['commands'][ value ]['mod'] = False
									self.message( _(">4 Now1 \"%s\" 4is for all users") % value, chan )
								else:
									self.assets['commands'][ value ]['mod'] = True
									self.message( _(">4 Now1 \"%s\" 4is only for bot users") % value, chan )
							else:
								self.message( _("> %s 4is unknow command to me") % value, chan )
						else:
							self.message(_(">4 This is not allowed."), chan)
					else:
						self.message('7Syntax:1 %s%s %s %s <command>' % ( prx, cmd, place, param ), chan )
				else:
					self.message(_('7Syntax:1 %s%s %s <turn/ignore/formod>') % ( prx, cmd, place ), chan )
			else:
				self.message(_('7Syntax:1 %s%s <osu/stats/commands>') % (prx, cmd), chan )
		else:
			self.message(_('7Syntax:1 %s%s <osu/stats/commands>') % (prx, cmd), chan )
	
	else:
		onCommand(self, chan, user, cmd, text)
	
def onCommand(self, chan, user, cmd, text):
	if self.assets['config']['use_langs'].get('es_ES') and user in self.assets['config']['use_langs']['es_ES']:
		_ = strings["es_ES"].gettext
	else:
		_ = strings["en_US"].gettext
	
	prx = self.assets['config']['prefix']
	
	if cmd == 'commands':
		buffer = ""
		is_mod = False
		if user in self.assets['config']['mods']: is_mod = True
		for cmds in self.assets['commands']:
			if self.assets['commands'][ cmds ]['active'] != False and chan not in self.assets['commands'][ cmds ]['ignore']:
				if self.assets['commands'][ cmds ]['mod'] and is_mod == False: pass
				else: buffer += prx + cmds + ", "
		if len( self.assets['commands'] ) > 0: self.message('>> %s' % buffer[:len(buffer)-2], chan)
		else: self.message( _('>> No Commands Found.'), chan)
		
	elif cmd == 'setlang':
		if len(text) > 0:
			if text in LANG:
				if user in self.assets['config']['use_langs'][text]:
					self.message(_("10>4 You already using this language"), chan)
				else:
					self.assets['config']['use_langs'][text].append(user)
					tmp = self.assets['config']['use_langs']
					for x in list(tmp):
						if x != text:
							if user in self.assets['config']['use_langs'][x]:
								the_list = self.assets['config']['use_langs'][x]
								self.assets['config']['use_langs'][x] = []
								for _user in list(the_list):
									if _user != user:
										self.assets['config']['use_langs'][x].append(_user)
					self.message(_("10>1 %s 14change your own language to1 %s") % (user, text), chan)
			else:
				self.message(_("7Syntax:1 %s%s %s") % (prx, cmd, ", ".join(LANG)), chan)
		else:
			self.message(_("7Syntax:1 %s%s %s") % (prx, cmd, ", ".join(LANG)), chan)
	
	elif cmd == 'bot':
		i = util.getinfo()
		self.message(_('11>1 %s v%s by NT5 3-1 Python %s 3-1 System6:1 %s %s %s 3-1 Uptime6:1 %s 3-1 Channels6:1 %i') % ( self.nick, self.version, sys.version.splitlines()[0], i[0], i[2], i[4], util.getDHMS( int( int( time.time() ) - self.uptime )), len( self.channels )), chan )
		
	elif cmd == 'uptime':
		self.message( _('11>1 %s Uptime: %s') % (self.nick, util.getDHMS( int( int( time.time() ) - self.uptime ))), chan)
	
	elif cmd == '8ball':
		if len(text) > 0:
			bases = [_("The answer lies in your heart"), _("I do not know"), _("Almost certainly"), _("No"), _("Instead, ask why you need to ask"), _("Go away. I do not wish to answer at this time"), _("Time will only tell")]
			self.message("> 10%s" % random.choice(bases), chan)
		else:
			self.message(_("7Syntax:1 %s%s <question>") % (prx, cmd), chan)
			
	elif cmd == 'stats':
		if len( text ) > 0: user = text
		if self.assets['stats'].get( user ):
			u = self.assets['stats'][ user ]
			Time = int( time.time() ) - u['seen']
			self.message( _("> %s 10Stats ago13:1 %s 3-10 Letters13:1 %s 10Words13:1 %s 10Lines13:1 %s 10Smiles13:1 %s 3-1 \"%s...\"") % ( user, util.getDHMS( Time ) if Time >= 2 else _("now"), util.group( int( u['letters'] ) ), util.group( int( u['words'] ) ), util.group( int( u['lines'] ) ), util.group( int( u['smiles'] ) ), u['quote'][:50] ), chan )
		else:
			self.message( _("> %s 4is unknown name to me") % user, chan )
			
	elif cmd == 'away':
		if self.assets['aways'].get( user ):
			self.message( _(">10 %s 14is back from6:1 %s. 14Time13:1 %s") % ( user, self.assets['aways'][ user ]['reason'], util.getDHMS( int( int( time.time() ) - self.assets['aways'][ user ]['time'] )) ), chan )
		if len( text ) > 0: reason = text
		else: reason = _("None")
		self.assets['aways'][ user ] = { "reason": reason, "time": int( time.time() ) }
		self.message( _(">10 %s 14is now away, reason13:1 %s") % ( user, reason ), chan )
		
	elif cmd == 'back':
		if self.assets['aways'].get( user ):
			self.message( _(">10 %s 14is back from6:1 %s. 14Time13:1 %s") % ( user, self.assets['aways'][ user ]['reason'], util.getDHMS( int( int( time.time() ) - self.assets['aways'][ user ]['time'] )) ), chan )
			self.assets['aways'].pop( user )
		else:
			self.message( _("> 4Error 3- 14You not have away status."), chan )
			
	
	elif cmd == 'afk':
		if len( text ) > 0:
			if self.assets['aways'].get( text ):
				x = self.assets['aways'].get( text )
				self.message( _(">10 %s 3- 14reason13:1 %s 3- 14Time13:1 %s") % ( text, x['reason'], util.getDHMS( int( int( time.time() ) - x['time'] )) ), chan )
			else:
				self.message( _(">10 %s 14not have away status.") % text, chan )
		else:
			if len( self.assets['aways'] ) > 0:
				c_channel = 0
				for x in self.names[ chan ]:
					if self.assets['aways'].get( x ):
						c_channel += 1
						self.message( _(">10 %s 3- 14reason13:1 %s 3- 14Time13:1 %s") % ( x, self.assets['aways'][ x ]['reason'], util.getDHMS( int( int( time.time() ) - self.assets['aways'][ x ]['time'] )) ), chan )
				if c_channel == 0:
					self.message( _(">14 Anybody from this channel have away status"), chan )
			else:
				self.message( _(">14 Anybody from this channel have away status"), chan )
	
	elif cmd == 'quote':
		if len( text ) > 0:
			param = text.split(' ')[0]
			text = text[len(param)+1:]
			if util.isInt( param ):
				try:
					q = self.assets['quotes'][ int( param ) ]
					self.message( _("> 10Quote [%i/%i]1 \"%s\" 3- 10by13:1 %s 3- 10Saved13:1 %s") % ( int( param ), len( self.assets['quotes'] ) - 1, q['text'], q['author'], util.getDHMS( int( int( time.time() ) - q['date'] )) ), chan )
				except:
					self.message( _(">4 %i is unknown quote to me.") % int( param ), chan )
			elif param == 'last':
				if len( self.assets['quotes'] ) > 0:
					q = self.assets['quotes'][ len( self.assets['quotes'] ) - 1 ]
					self.message( _("> \"%s\" 3- 10by13:1 %s 3-10 Saved13:1 %s") % ( q['text'], q['author'], util.getDHMS( int( int( time.time() ) - q['date'] )) ), chan )
				else:
					self.message( _(">4 No quotes found."), chan )
			elif param == 'add' and len( text ) > 0:
				try:
					self.assets['quotes'].append( { "text": text, "author": user, "date": int( time.time() ) } )
					self.message( _(">10 Quote [%i/%i] 3-1 \"%s\" 3-10 by13:1 %s") % ( (len( self.assets['quotes'] ) - 1), (len( self.assets['quotes'] ) - 1), text, user ), chan )
				except Exception, e:
					self.message(_("> 4Can't save quote. reason: %s ") % str( e ), chan )
			elif param == 'del' and util.isInt( text ) and user in self.assets['config']['mods']:
				try:
					self.message( _("> 10Quote1 \"%s\" 10id13:1 %i 10is now delete from bot.") % ( self.assets['quotes'][ int( text ) ]['text'], int( text ) ), chan )
					self.assets['quotes'].pop( int( text ) )
				except Exception, e:
					self.message( _(">4 %i is unknown quote to me.") % ( int( text ) ), chan )
			else:
				self.message(_("7Syntax:1 %s%s <add/del/last/quoute id>") % (prx, cmd), chan)
		else:
			if len( self.assets['quotes'] ) == 0:
				self.message(_("7Syntax:1 %s%s <add/del/last/quoute id>") % (prx, cmd), chan)
			else:
				q = random.choice( self.assets['quotes'] )
				self.message( _("> \"%s\" 3- 10by13:1 %s 3-10 Saved13:1 %s") % ( q['text'], q['author'], util.getDHMS( int( int( time.time() ) - q['date'] )) ), chan )
	
	elif cmd == 'twitch':
		if len(text) > 0: user = text.split(' ')[0]
		try:
			headers = { 'Accept': 'application/vnd.twitchtv.v3+json', 'Accept-Charset': 'utf-8' }
			q = dict(
				channel = util.json_request( self.assets['api']['twitch']['request'][0] % (self.assets['api']['twitch']['url'], user), headers ),
				follows = util.json_request( self.assets['api']['twitch']['request'][1] % (self.assets['api']['twitch']['url'], user), headers ),
				stream = util.json_request( self.assets['api']['twitch']['request'][2] % (self.assets['api']['twitch']['url'], user), headers )
			)
			if q['stream']['stream'] != "None": if_stream = _("Online 3- 14Current Views13:1 %s") % util.group( int ( q['stream']['stream']['viewers'] ) )
			else: if_stream = _("Offline")
			if q['follows']['_total'] > 0: if_follows = _("3- 14Last Follows13:1 %s") % q['follows']['follows'][0]['user']['display_name'].decode("utf-8")
			else: if_follows = ""
			MSG = (_("10> 14Name13:1 %s 3- 14Link13:12 %s 3- 14Channel Views13:1 %s 3- 14Follows13:1 %s 3- 14Game13:1 %s 3- 14Title13:1 %s 3- 14Status13:1 %s %s")) % ( q['channel']['display_name'].decode("utf-8"), q['channel']['url'].decode("utf-8"), util.group( int( q['channel']['views'] ) ), util.group( int( q['follows']['_total'] ) ), q['channel']['game'].decode("utf-8"), q['channel']['status'].replace('\n','').decode("utf-8"), if_stream, if_follows )			
			self.message(MSG, chan)
		except Exception, e:
			self.message(_("4Unknown User"), chan)
	
	elif cmd == 'ctwitch':
		if chan in self.assets['config']['single_channel']:
			if self.assets['config']['single_channel'][chan].get('twitch_control'):
				if user in self.assets['config']['single_channel'][chan]['twitch_control']['users']:
					if len( text ) > 0:
						param = util.gettext(text, 0)
						def _dotwitch(send, data):
							opener = urllib2.build_opener(urllib2.HTTPHandler)
							request = urllib2.Request('%skraken/channels/%s' % (self.assets['api']['twitch']['url'], self.assets['config']['single_channel'][chan]['twitch_control']['api']['user']), data='channel[%s]=%s' % (data, send.replace(' ', '+')))
							request.add_header('Accept', 'application/vnd.twitchtv.v3+json')
							request.add_header('Authorization', 'OAuth %s' % self.assets['config']['single_channel'][chan]['twitch_control']['api']['key'])
							request.get_method = lambda: 'PUT'
							url = opener.open(request)
						if param == 'game': 
							if util.gettext(text, 1):
								game = text[len(param)+1:]
								try:
									_dotwitch(urllib2.quote(game.encode('utf-8')), 'game')
									self.message(_("10> 14Game was change to13:1 %s") % game, chan)
								except Exception, e: self.message(_("4Error occurred :("), chan)
							else:
								self.message(_("7Syntax:1 %s%s <game/title> <parameter>") % (prx, cmd), chan)
						elif param == 'title':
							if util.gettext(text, 1):
								title = text[len(param)+1:]
								try:
									_dotwitch(urllib2.quote(title.encode('utf-8')), 'status')
									self.message(_("10> 14Title set to13:1 %s") % title, chan)
								except Exception, e: self.message(_("4Error occurred :("), chan)
							else:
								self.message(_("7Syntax:1 %s%s <game/title> <parameter>") % (prx, cmd), chan)
						else:
							self.message(_("7Syntax:1 %s%s <game/title> <parameter>") % (prx, cmd), chan)
					else:
						self.message(_("7Syntax:1 %s%s <game/title> <parameter>") % (prx, cmd), chan)
				else:
					self.message(_("10> 4You do not have permission to use this command."), chan)
			else:
				self.message(_("10> 4This channel is not configured to use this command!"), chan)
		else:
			self.message(_("10> 4This channel is not configured to use this command!"), chan)
	
	elif cmd == 'osurequest':
		if chan in self.assets['config']['single_channel']:
			if self.assets['config']['single_channel'][chan].get('osu_req') and self._banchonet:
				if len( text ) > 0:
					if self.assets['config']['single_channel'][chan]['osu_req']['active']:
						if util.isOsuLink( text ):
							for _user in self.assets['config']['single_channel'][chan]['osu_req']['users']:
								self._banchonet.send("PRIVMSG %s :[REQUEST] [%s]: %s" % (_user, user, text))
							self.message(_("10> 14Your request was sent13:1 \"%s\" 14to13:1 %s") % (text, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users'])), chan)
						else:
							self.message(_("10> 4Invalid link!"), chan)
					else:
						self.message(_("10> 4The requests are turned off."), chan)
				else:
					self.message(_("7Syntax:1 %s%s <osu link>") % (prx, cmd), chan)
			else:
				self.message(_("10> 4This channel is not configured to use this command!"), chan)
		else:
			self.message(_("10> 4This channel is not configured to use this command!"), chan)
	
	elif cmd == 'vcmp':
		if len( text ) > 0:
			if util.gettext( text, 0 ) == 'add' and user in self.assets['config']['mods']:		
				name = util.gettext( text, 1 )
				server = util.gettext( text, 2 )
				ip = util.gettext( server, 0, ':' )
				port = util.gettext( server, 1, ':' )
				if ip and port:
					if self.assets['config']['vcmp_servers'].get( name ):
						self.assets['config']['vcmp_servers'][ name ]['ip'] = str( ip )
						self.assets['config']['vcmp_servers'][ name ]['port'] = int( port )
					else:
						self.assets['config']['vcmp_servers'].setdefault( name, { "ip": str( ip ), "port": int( port ) } )
					self.message( _("10> 3Server1 \"%s\" 3has been saved,1 %s%s %s") % ( name, prx, cmd, name ), chan )
				else:
					self.message(_('7Syntax:1 %s%s add <ServerName> <IP:PORT>') % ( prx, cmd ), chan )
			elif util.gettext( text, 0 ) == 'del' and user in self.assets['config']['mods']:
				if util.gettext( text,1 ):
					if self.assets['config']['vcmp_servers'].get( util.gettext( text, 1 ) ):
						self.assets['config']['vcmp_servers'].pop( util.gettext( text, 1 ) )
						self.message( _("10>1 \"%s\" 4is now removed from server list") % util.gettext( text, 1 ), chan )
					else:
						self.message( _("10>1 \"%s\" 4is unknown server to me") % util.gettext( text, 1 ), chan )
				else:
					self.message(_('7Syntax:1 %s%s del <ServerName>') % ( prx, cmd ), chan )
			elif util.gettext( text, 0 ) == 'list':
				if len( self.assets['config']['vcmp_servers'] ) > 0:
					self.message( "%s%s <%s>" % ( prx, cmd, ", ".join(self.assets['config']['vcmp_servers']) ), chan )
				else:
					self.message( _("10>4 No have any server saved."), chan )
			elif self.assets['config']['vcmp_servers'].get( util.gettext( text, 0 ) ):
				ip = self.assets['config']['vcmp_servers'][ util.gettext( text, 0 ) ]['ip']
				port = self.assets['config']['vcmp_servers'][ util.gettext( text, 0 ) ]['port']
				q = vcmpQuery( None, str( ip ), int( port ) )
				if q:
					try:
						q.connect()
						info = q.getInfo()
						try: players = q.getBasicPlayers()
						except: players = []
						player_string = ""
						if len( players ) > 0:
							for x in players: player_string += "%s6:7 %i1, " % ( x['name'], x['score'] )
						self.message( _("10>1 %s 3- 10Server6:1 %s 10IP6:1 %s:%s 10Gamemode6:1 %s 10Players6:1 [%i/%i] %s") % ( util.gettext( text, 0 ), info['hostname'], str(ip), str(port), info['gamemode'], info['players'], info['maxplayers'], _('4Close') if info['password'] == 1 else _('3Open')), chan )
						if len( player_string ) > 0:
							self.message( player_string[:len(player_string)-2], chan )
					except Exception, e:
						self.message( _("10>4 Unknown server"), chan )
				q.close()
			else:
				ip = util.gettext( text, 0, ':' )
				port = util.gettext( text, 1, ':' )
				if ip and port:
					q = vcmpQuery( None, str( ip ), int( port ) )
					if q:
						try:
							q.connect()
							info = q.getInfo()
							try: players = q.getBasicPlayers()
							except: players = []
							player_string = ""
							if len( players ) > 0:
								for x in players: player_string += "%s6:7 %i1, " % ( x['name'], x['score'] )
							self.message( _("10> 10Server6:1 %s 10Gamemode6:1 %s 10Players6:1 [%i/%i] %s") % ( info['hostname'], info['gamemode'], info['players'], info['maxplayers'], _('4Close') if info['password'] == 1 else _('3Open')), chan )
							if len( player_string ) > 0:
								self.message( player_string[:len(player_string)-2], chan )
						except Exception, e:
							self.message( _("10>4 Unknown server"), chan )
					q.close()
				else:
					self.message(_('7Syntax:1 %s%s %s') % ( prx, cmd, '<list/add/del/IP:PORT/Server Name>' if user in self.assets['config']['mods'] else '<list/IP:PORT/Server Name>' ), chan)
		else:
			self.message(_('7Syntax:1 %s%s %s') % ( prx, cmd, '<list/add/del/IP:PORT/Server Name>' if user in self.assets['config']['mods'] else '<list/IP:PORT/Server Name>' ), chan)
	
	elif cmd == 'weather':
		if len( text ) > 0:
			try:
				q = util.json_request( self.assets['api']['weather']['request'] % ( self.assets['api']['weather']['url'], urllib2.quote( text.encode("utf-8") ) ), {} )
				self.message( _(u"11>1 %s %s 3-5 %s 3- 14Coord13:1 %s, %s 3- 14Temp13:1 %s14c 3- 14Humidity13:1 %s%% 3- 14Pressure13:1 %s14hPa 3- 14Wind13:1 %s14mps") % ( q['name'], q['sys']['country'], q['weather'][0]['description'], str(q['coord']['lat']), str(q['coord']['lon']), str( ( int( q['main']['temp'] ) - 273.15 ) * 1.0000 ), str(q['main']['humidity']), util.group( int( q['main']['pressure'] ) ), str(q['wind']['speed']) ), chan )
			except Exception, e:
				self.message( _("4Search failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
			
	elif cmd == 'translate':
		if len( text ) > 0:
			result, code, string = util.get_google_translate( text, 'en' )
			if code == 'en' or result == False:
				result, code, string = util.get_google_translate( text, 'es' )
			if result:
				self.message( _("13> 14Translate from1 %s13:1 \"%s\".") % (code, string), chan )
			else:
				self.message( _("13> 4Can't translate text1 %s") % (string), chan )
		else:
			self.message(_("7Syntax:1 %s%s <string>") % (prx, cmd), chan)
	
	elif cmd == 'facebook':
		if len( text ) > 0:
			search = str( urllib2.quote( text.encode("utf-8") ) )
			try:
				messages = []
				q = util.json_request( self.assets['api']['facebook']['request'][0] % ( self.assets['api']['facebook']['url'], search ), {} )
				if q.get( "username" ): messages.append( _("10Username6:1 %s") % q['username'] )
				if q.get( "name" ): messages.append( _("10Name6:1 %s") % q['name'].decode("unicode-escape") )
				if q.get( "id" ): messages.append( _("10Link6:1 http://www.facebook.com/profile.php?id=%s") % q['id'] )
				if q.get( "gender" ): messages.append( _("10Gender6:1 %s") % q['gender'] )
				if q.get( "locale" ): messages.append( _("10Locale6:1 %s") % q['locale'] )
				if q.get( "about" ): messages.append( _("10About6:1 %s") % q['about'].decode("unicode-escape") )
				if q.get( "category" ): messages.append( _("10Category6:1 %s") % q['category'].decode("unicode-escape") )
				if q.get( "likes" ): messages.append( _("10Likes6:1 %s") % util.group( int( q['likes'] ) ) )
				if q.get( "talking_about_count" ): messages.append( _("10Talking About6:1 %s") % util.group( int( q['talking_about_count'] ) ) )
				
				self.message( "> %s" % " 3- ".join( messages ), chan )
			except Exception, e:
				self.message( _("4Some of the aliases you requested do not exist:1 %s") % text.encode("utf-8"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <user name/id>") % (prx, cmd), chan)
			
	elif cmd == 'osu':
		if len(text) > 0: user = text.split(' ')[0]
		else: user = 'NT5_projectd'
		try:
			q = util.json_request( self.assets['api']['osu']['request'] % ( self.assets['api']['osu']['url'], self.assets['api']['osu']['key'], user ), {} )[0]
			self.message( _("> 6%s 3- 14Country6: 1%s 3- 14Play Count6:1 %s 3- 14Ranked Score6:1 %s 3- 14Total Score6:1 %s 3- 14Level6:1 %d 3- 14Accuracy6:1 %0.f%% 3- 14PP6:1 %0.f 3- 14Rank6:1 #%s") % ( q['username'], q['country'], util.group( int(q['playcount']) ), util.group( int(q['ranked_score']) ), util.group( int(q['total_score']) ), float( q['level'] ), float( q['accuracy']) , float( q['pp_raw'] ), util.group( int( q['pp_rank']) ) ), chan )
		except:
			self.message(_("4Unknown User"), chan)
	
	elif cmd == 'animeflv':
		if len( text ) > 0:
			try:
				page = util.web_request( self.assets['api']['animeflv']['request'] % ( self.assets['api']['animeflv']['url'], urllib2.quote( text.encode("utf-8") ) ) )
				lktitulo = re.compile( "<a href=\"(?:(.+))\" * title=\"(?:(.+))\">", re.UNICODE )
				lktitulo = lktitulo.findall( page )
				sinopsis = re.compile("<div class=\"sinopsis\">(?:(.+))<\/div>", re.UNICODE)
				sinopsis = sinopsis.findall( page )
				self.message( _("> 10Title6:1 %s 3- 10Link6: 12%s%s 3- 10Sinopsis6:1 %s") % ( util.NoHTML(lktitulo[0][1].decode('utf-8')), self.assets['api']['animeflv']['url'][:-1], util.NoHTML(lktitulo[0][0].decode('utf-8')), util.NoHTML(sinopsis[0].decode('utf-8')) ), chan )
			except Exception, e:
				self.message( _("4Search Failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
			
	elif cmd == 'konachan':
		if len(text) > 0:
			try:
				q_ = util.json_request( self.assets['api']['konachan']['request'] % ( self.assets['api']['konachan']['url'], text.replace(' ', '_')  ), {} )
				id = random.randrange( 0, len( q_ ) )
				q = q_[ id ]
				self.message(_("[%i/%i] 10Author13:1 %s 3- 10Link13:12 %s") % ( id, len( q_ ), str(q['author']), str(q['file_url']) ), chan)
			except Exception, e:
				self.message( _("4Search Failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
	
	elif cmd == 'danbooru':
		if len(text) > 0:
			try:
				q_ = util.json_request( self.assets['api']['danbooru']['request'][0] % ( self.assets['api']['danbooru']['url'], text.replace(' ', '_') ), {} )
				id = random.randrange( 0, len( q_ ) )
				q = q_[ id ]
				self.message(_("[%i/%i] 10Author13:1 %s 3- 10Link13:12 %s") % ( id, len( q_ ), q['uploader_name'].decode("unicode-escape"), self.assets['api']['danbooru']['url'][:-1]+q['file_url'] ), chan)
			except Exception, e:
				self.message( _("4Search Failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
			
	elif cmd == 'wdanbooru':
		if len(text) > 0:
			try:
				q = util.json_request( self.assets['api']['danbooru']['request'][1] % ( self.assets['api']['danbooru']['url'], text.replace(' ', '_') ), {} )[0]
				info = q['body'].split("\r\n\r\n")
				if len(info) <= 1: info = info[0]
				else: info = info[1]
				info = info.replace("\r\n","")
				self.message( _(">14 %s... 3-12 %swiki_pages/%s10 by13:1 %s") % ( info[:200].decode('unicode-escape'), self.assets['api']['danbooru']['url'], q['id'], q['creator_name'].decode('unicode-escape') ), chan )
			except Exception, e:
				self.message( _("4Search Failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
	
	elif cmd == 'redtube':
		if len(text) < 0: sq = ""
		else: sq = urllib2.quote( text.encode("utf-8") )
		try:
			q = util.json_request( self.assets['api']['redtube']['request'] % ( self.assets['api']['redtube']['url'], sq.replace(' ', '+') ), {} )
			q_ = q['videos'][0]['video']
			self.message( _("<4Red0,1Tube> 10Search13:1 %s 3- 10Title13:1 %s 3- 10Duration13:1 %s 3- 10Rating13:1 %s 3- 10Views13:1 %s 3- 10Link13:1 12%s 3- 10Image13:12 %s") % ( util.group( int( q['count'] ) ), util.NoHTML(q_['title']), q_['duration'], str(q_['rating']), util.group( int(q_['views']) ), q_['url'].replace("\\",""), q_['default_thumb'].replace("\\","") ), chan )
		except Exception, e:
			self.message( _("4Search Failed"), chan )
	
	elif cmd == 'youtube':
		if len(text) < 0: sq = ""
		else: sq = urllib2.quote( text.encode("utf-8") )
		try:
			q = util.json_request( self.assets['api']['youtube']['request'] % ( self.assets['api']['youtube']['url'], sq.replace(' ', '+'), self.assets['api']['youtube']['key'] ), {} )
			sp = q['items'][0]['snippet']
			self.message( _(">1,0You0,4Tube< Title:4 %s - 10Description:4 %s - 10Link:2  http://www.youtube.com/watch?v=%s - 10By:4 %s") % ( util.NoHTML(sp['title'].decode("utf-8")), util.NoHTML(sp['description'].decode("utf-8")), q['items'][0]['id']['videoId'], sp['channelTitle'].decode("utf-8") ), chan )
		except Exception, e:
			self.message( _("4Search Failed"), chan )
	
	if cmd == 'google':
		if len(text) > 0:
			try:
				gs = GoogleSearch( text.encode("utf-8") )
				gs.results_per_page = 50
				results = gs.get_results()
				self.message( _('2G4o7o2g3l4e 10Search: 14%s 3- 14%s 3- 12%s') % ( results[0].title.encode("utf8"), results[0].desc.encode("utf8"), results[0].url.encode("utf8") ), chan )
			except:
				self.message( _("4Search failed"), chan )
		else:
			self.message(_("7Syntax:1 %s%s <search>") % (prx, cmd), chan)
			