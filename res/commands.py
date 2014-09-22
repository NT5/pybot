#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

import gettext
import util as util, sys, time, random, urllib2, re

#Game Query
from vcmpQuery import vcmpQuery
from MCQuery import MinecraftQuery

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
	_ = util.GetLangStrings( self, strings, user, chan )
	
	prx = self.assets['config']['prefix']
	if cmd == 'exe':
		if len(text) > 0:
			try: exec text
			except Exception, e:
				self.message( _('4Error:1 %s') % str( e ), chan )	
		else:
			self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s <python>" % (prx, cmd)), chan)
			
	elif cmd == 'adduser':
		if len(text) > 0:
			text2 = text.split(' ')[0]
			if text2 in self.assets['config']['mods']:
				self.message(_("10>1 %s is already in a bot list.") % text2, chan)
			else:
				self.assets['config']['mods'].append( text2 )
				self.message(_("10>1 %s is now a bot user.") % text2, chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s <user> [%s]" % (prx, cmd, ", ".join(self.assets['config']['mods']))), chan)
	
	elif cmd == 'deluser':
		if len(text) > 0:
			exclude = text.split(' ')[0]
			if exclude in self.assets['config']['mods']:
				tmp = self.assets['config']['mods']
				self.assets['config']['mods'] = []
				for x in list(tmp):
					if x != exclude: self.assets['config']['mods'].append( x )
				self.message(_("10>1 %s is no longer a bot user") % exclude, chan)
			else:
				self.message(_("10>1 %s unknown name, Current Users: %s") % (exclude, ", ".join(self.assets['config']['mods'])), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s <user> [%s]" % (prx, cmd, ", ".join(self.assets['config']['mods']))), chan)
	
	elif cmd == 'control':
		if len(text) > 0:
			place = util.gettext( text, 0 )
			param = util.gettext( text, 1 )
			value = util.gettext( text, 2 )
			if place == 'stats':
				if param == 'del':
					if value:
						if self.assets['stats']['users'].get( value ):
							self.message( _("> %s 4has been deleted from user stats.") % value, chan )
							self.assets['stats']['users'].pop( value )
						elif self.assets['stats']['channels'].get( value ):
							self.message( _("> %s 4has been deleted from channel stats") % value, chan )
							self.assets['stats']['channels'].pop( value )
						else:
							self.message( _("> %s 4is a unknown name to me") % value, chan )
					else:
						self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s %s %s <user>" % (prx, cmd, place, param)), chan)
				elif param == 'clean':
					_dataclear = { 'users': 0, 'words': 0, 'links': 0, 'channels': 0 }
					_range = self.assets['config']['wordstats']['clean_range']
						
					for _user in list( self.assets['stats']['users'] ):
						if int( time.time() ) - self.assets['stats']['users'][ _user ]['seen'] > _range:
							self.assets['stats']['users'].pop( _user )
							_dataclear['users'] += 1
							
					for _chan in list( self.assets['stats']['channels'] ):
						if int( time.time() ) - self.assets['stats']['channels'][ _chan ]['seen'] > _range:
							self.assets['stats']['channels'].pop( _chan )
							_dataclear['channels'] += 1
							
					for word in list( self.assets['stats']['words'] ):
						if int( time.time() ) - self.assets['stats']['words'][ word ]['time'] > _range or self.assets['stats']['words'][ word ]['uses'] <= 5:
							self.assets['stats']['words'].pop( word )
							_dataclear['words'] += 1
							
					for link in list( self.assets['stats']['links'] ):
						if int( time.time() ) - self.assets['stats']['links'][ link ]['time'] > _range or self.assets['stats']['links'][ link ]['uses'] <= 3:
							self.assets['stats']['links'].pop( link )
							_dataclear['links'] += 1
							
					self.message( _("11>4 Stats cleaned 1(%s)13:1 %s 4Users 3-1 %s 4Words 3-1 %s 4Links 3-1 %s 4Channels") % ( util.getDHMS( _range ), util.group(_dataclear['users']), util.group(_dataclear['words']), util.group(_dataclear['links']), util.group(_dataclear['channels']) ), chan )
				elif param == 'ignore':
					if value:
						if value in self.assets['config']['wordstats']['ignore']:
							id = self.assets['config']['wordstats']['ignore'].index( value )
							self.assets['config']['wordstats']['ignore'].pop( id )
							self.message(_("> %s 4is no longer on ignore list") % value, chan)
						else:
							self.assets['config']['wordstats']['ignore'].append( value )
							self.message( _("> %s 4is now on ignore list") % value, chan )
					else:
						self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s %s %s <user>" % (prx, cmd, place, param)), chan)
				else:
					self.message(_("7Syntax:1 {syntax}").format(syntax = "%s%s %s <del/clean/ignore>" % (prx, cmd, place)), chan)
			elif place == 'osu':
				if param == 'request':
					_osu_user = " ".join(text.split(' ')[3:]).replace(" ", "_")
					if value == 'set':
						if len( _osu_user ) > 0:
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get("osu_req"):
									if _osu_user in self.assets['config']['single_channel'][chan]["osu_req"]['users']:
										self.message(_("10>1 \"%s\" 4is already on the channel's list") % _osu_user, chan)
									else:
										self.assets['config']['single_channel'][chan]["osu_req"]['users'].append(_osu_user)
								else:
									self.assets['config']['single_channel'][chan].setdefault( "osu_req", { "active": True, "users": [_osu_user] } )
							else:
								self.assets['config']['single_channel'].setdefault( chan, { "osu_req": { "active": True, "users": [_osu_user] } } )
							self.message( _("10> 14Osu request set to1 %s 14and send to13:1 %s on BanchoNet") % ( chan, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users']) ), chan )
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <user>" % (prx, cmd, place, param, value)), chan)
					elif value == 'del':
						if len( _osu_user ) > 0:
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get("osu_req"):
									if _osu_user in self.assets['config']['single_channel'][chan]['osu_req']['users']:
										if len(self.assets['config']['single_channel'][chan]['osu_req']['users']) > 1:
											id = self.assets['config']['single_channel'][chan]['osu_req']['users'].index(_osu_user)
											self.assets['config']['single_channel'][chan]['osu_req']['users'].pop(id)
											self.message(_("10>1 \"%s\" 4deleting channel from1 %s") % (_osu_user, chan), chan)
										else:
											self.assets['config']['single_channel'][chan].pop('osu_req')
											if len(self.assets['config']['single_channel'][chan]) == 0:
												self.assets['config']['single_channel'].pop(chan)
											self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (_osu_user, chan), chan)
									else:
										self.message( _("> %s 4is a unknown name to me") % _osu_user, chan )
								else:
									self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
							else:
								self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <user>" % (prx, cmd, place, param, value)), chan)
					elif value == 'remove':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								_users = self.assets['config']['single_channel'][chan]['osu_req']['users']
								self.assets['config']['single_channel'][chan].pop('osu_req')
								if len(self.assets['config']['single_channel'][chan]) == 0:
									self.assets['config']['single_channel'].pop(chan)
								self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (", ".join(_users), chan), chan)
							else:
								self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
					elif value == 'turn':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								_Ac = self.assets['config']['single_channel'][chan]['osu_req']['active']
								if _Ac == True: self.assets['config']['single_channel'][chan]['osu_req']['active'] = False
								else: self.assets['config']['single_channel'][chan]['osu_req']['active'] = True
								self.message(_("10>14 Osu!request has been turned %s, at1 %s") % ( _("off") if _Ac == True else _("on"), chan ), chan)
							else:
								self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
					elif value == 'get':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get("osu_req"):
								self.message(_("10> 13Osu!request14 at1 %s 14has been sent to1 %s") % ( chan, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users'])), chan)
							else:
								self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
						else:
							self.message( _("10>1 %s 4is a unknown channel to me") % chan, chan )
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s <set/del/remove/turn/get>" % (prx, cmd, place)), chan)
				elif (param == 'bancho') | (param == 'np') | (param == 'lastfm'):
					_osu_chan = util.gettext( text, 3 )
					_osu_user = " ".join(text.split(' ')[4:]).replace(" ", "_")
					if param == 'bancho': _sec = 'bancho_listen'
					elif param == 'lastfm': _sec = 'last_fm'
					else: _sec = 'osu_np'
					if value:
						if value == 'set':
							if _osu_chan and str(_osu_chan)[0] == "#":
								if len( _osu_user ) > 0:
									if self.assets['config'][_sec].get(_osu_user):
										if _osu_chan in self.assets['config'][_sec][_osu_user]:
											self.message(_("10>1 \"%s\" 4is already on the user's list") % _osu_chan, chan)
										else:
											self.assets['config'][_sec][_osu_user].append(_osu_chan)
									else:
										self.assets['config'][_sec].setdefault(_osu_user, [_osu_chan])
										if param == 'np':
											self.message("> %s Post KEY: %s" % (_osu_user, cryp.encode(_osu_user)), user, type = "n")
									self.message( _("10>14Messages of1 %s 14have been sent to13:1 %s") % ( _osu_user, ", ".join(self.assets['config'][_sec][_osu_user]) ), chan )
								else:
									self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s %s <user>" % (prx, cmd, place, param, value, _osu_chan)), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <#channel>" % (prx, cmd, place, param, value)), chan)
						elif value == 'del':
							if _osu_chan and str(_osu_chan)[0] == "#":
								if len( _osu_user ) > 0:
									if self.assets['config'][_sec].get(_osu_user):
										if _osu_chan in self.assets['config'][_sec][_osu_user]:
											if len(self.assets['config'][_sec][_osu_user]) > 1:
												id = self.assets['config'][_sec][_osu_user].index(_osu_chan)
												self.assets['config'][_sec][_osu_user].pop(id)
												self.message(_("10>1 \"%s\" 4deleting channel from1 %s") % (_osu_chan, _osu_user), chan)
											else:
												self.assets['config'][_sec].pop( _osu_user )
												self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (_osu_user, _sec), chan)
										else:
											self.message( _("10>1 %s 4is a unknown channel to me") % _osu_chan, chan )
									else:
										self.message( _("> %s 4is a unknown name to me") % _osu_user, chan )
								else:
									self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s %s <user>" % (prx, cmd, place, param, value, _osu_chan)), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <#channel>" % (prx, cmd, place, param, value)), chan)
						elif value == 'remove':
							_osu_user = " ".join(text.split(' ')[3:])
							if len( _osu_user ) > 0:
								if self.assets['config'][_sec].get(_osu_user) != None:
									self.assets['config'][_sec].pop( _osu_user )
									self.message(_("10>1 \"%s\" 4delete from1 \"%s\"") % (_osu_user, _sec), chan)
								else:
									self.message( _("> %s 4is a unknown name to me") % _osu_user, chan )
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <user>" % (prx, cmd, place, param, value)), chan)
						elif value == 'get':
							_osu_user = " ".join(text.split(' ')[3:])
							if len( _osu_user ) > 0:
								if self.assets['config'][_sec].get(_osu_user) != None:
									self.message( _("10>14Messages of1 %s 14have been sent to13:1 %s") % ( _osu_user, ", ".join(self.assets['config'][_sec][_osu_user]) ), chan )
									if param == 'np':
										self.message("> %s Post KEY: %s" % (_osu_user, cryp.encode(_osu_user)), user, type = "n")
								else:
									self.message( _("> %s 4is a unknown name to me") % _osu_user, chan )
							else:
								self.message(_('10> 14All users of1 \"%s\"13:1 %s') % ( _sec, ", ".join(self.assets['config'][_sec]) ), chan )
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <set/del/remove/get>" % (prx, cmd, place, param)), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <set/del/remove/get>" % (prx, cmd, place, param)), chan)
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s <lastfm/bancho/np/request>" % (prx, cmd, place)), chan)

			elif place == 'channel':
				if param == 'welcome':
					if value:
						if value == 'set':
							_message = " ".join(text.split(' ')[3:])
							if len(_message) > 0:
								try: _message = _message.decode("unicode-escape")
								except: pass
								if self.assets['config']['single_channel'].get(chan):
									if self.assets['config']['single_channel'][chan].get("welcome_msg"):
										self.assets['config']['single_channel'][chan]["welcome_msg"] = _message
									else:
										self.assets['config']['single_channel'][chan].setdefault("welcome_msg", _message)
								else:
									self.assets['config']['single_channel'].setdefault(chan, { "welcome_msg": _message })
								self.message(_("10>14 Welcome message from1 %s 14set at13:1 \"%s\"") % (chan, _message), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <message>" % (prx, cmd, place, param, value)), chan)
						elif value == 'remove':
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get("welcome_msg"):
									_message = self.assets['config']['single_channel'][chan]["welcome_msg"]
									self.assets['config']['single_channel'][chan].pop('welcome_msg')
									if len(self.assets['config']['single_channel'][chan]) == 0:
										self.assets['config']['single_channel'].pop(chan)
									self.message(_("10>1 \"%s\" 4remove from welcome message of1 %s") % (_message, chan), chan)
								else:
									self.message(_("10> 4This channel is not configured to use this command!"), chan)
							else:
								self.message(_("10> 4This channel is not configured to use this command!"), chan)
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <set/remove>" % (prx, cmd, place, param)), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <set/remove>" % (prx, cmd, place, param)), chan)
				elif param == 'join':
					if value and value[:1] == "#":
						self.Join( value )
						if value not in self.channels: self.channels.append( value )
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <#channel>" % (prx, cmd, place, param)), chan)
				elif param == 'part':
					if value and value[:1] == "#":
						self.Part( value )
						if value in self.channels: self.channels.pop( self.channels.index( value ) )
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <#channel>" % (prx, cmd, place, param)), chan)
				elif param == 'flood':
					if value == 'turn':
						if self.assets['config']['flood_protection']['enable']: self.assets['config']['flood_protection']['enable'] = False
						else: self.assets['config']['flood_protection']['enable'] = True
						self.message( _("10>14 Flood protection has been turned %s") % ( _("on") if self.assets['config']['flood_protection']['enable'] == True else _("off") ), chan )
					elif value == 'ignore':
						if chan in self.assets['config']['flood_protection']['ignore']: 
							self.assets['config']['flood_protection']['ignore'].pop( self.assets['config']['flood_protection']['ignore'].index( chan ) )
							self.message(_("> %s 4is no longer on ignore list") % chan, chan)
						else:
							self.assets['config']['flood_protection']['ignore'].append( chan )
							self.message( _("> %s 4is now on ignore list") % chan, chan )
					elif value == 'docmd':
						if self.assets['config']['flood_protection']['only_cmd']: self.assets['config']['flood_protection']['only_cmd'] = False
						else: self.assets['config']['flood_protection']['only_cmd'] = True
						self.message( _("10>14 Flood protection catch %s") % (_("only commands") if self.assets['config']['flood_protection']['only_cmd'] == True else _("all text with commands") ), chan )
					elif value == 'level':
						_level = util.gettext( text, 3 )
						_flood = self.assets['config']['flood_protection']
						if _level:
							if _level == 'high':
								_flood['block_time'] = 30
								_flood['max_reps'] = 3
								_flood['max_time'] = 10
								_flood['min_time'] = 1
								self.message( _("13> 4Flood protection established to %s level 14(Block Time: %isecs - Max Reps: %i - Max Time: %isecs - Min Time: %isecs)") % ( _level, _flood['block_time'], _flood['max_reps'], _flood['max_time'], _flood['min_time'] ), chan )
							elif _level == 'medium':
								_flood['block_time'] = 5
								_flood['max_reps'] = 5
								_flood['max_time'] = 5
								_flood['min_time'] = 1
								self.message( _("13> 4Flood protection established to %s level 14(Block Time: %isecs - Max Reps: %i - Max Time: %isecs - Min Time: %isecs)") % ( _level, _flood['block_time'], _flood['max_reps'], _flood['max_time'], _flood['min_time'] ), chan )
							elif _level == 'low':
								_flood['block_time'] = 3
								_flood['max_reps'] = 8
								_flood['max_time'] = 3
								_flood['min_time'] = 1
								self.message( _("13> 4Flood protection established to %s level 14(Block Time: %isecs - Max Reps: %i - Max Time: %isecs - Min Time: %isecs)") % ( _level, _flood['block_time'], _flood['max_reps'], _flood['max_time'], _flood['min_time'] ), chan )
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <high/medium/low>" % (prx, cmd, place, param, value)), chan)
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <high/medium/low>" % (prx, cmd, place, param, value)), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <turn/ignore/docmd/level>" % (prx, cmd, place, param)), chan)
				elif param == 'automessages':
					if value == 'set':
						_message = " ".join(text.split(' ')[3:])
						if len(_message) > 0:
							if self.assets['config']['single_channel'].get(chan):
								if self.assets['config']['single_channel'][chan].get('auto_msgs'):
									if _message in self.assets['config']['single_channel'][chan]['auto_msgs']['messages']:
										self.message(_("10>1 \"%s\" 4is already on the list of auto messages!") % _message, chan)
									else:
										self.assets['config']['single_channel'][chan]['auto_msgs']['messages'].append(_message)
								else:
									self.assets['config']['single_channel'][chan].setdefault( "auto_msgs", { "active": True, "messages": [_message] } )
									util.AutoMessages(self, False)
							else:
								self.assets['config']['single_channel'].setdefault(chan, { "auto_msgs": { "active": True, "messages": [_message] } })
								util.AutoMessages(self, False)
							buffer = ""
							i = 0
							for msg in self.assets['config']['single_channel'][chan]['auto_msgs']['messages']:
								buffer += "[%i] %s..., " % ( i, msg[:15] )
								i += 1
							self.message(_("10> 14Auto messages with13:1 %s 14and on a loop of 25min.") % (buffer[:len(buffer)-2]), chan)
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <message>" % (prx, cmd, place, param, value)), chan)
					elif value == 'del':
						id = util.gettext( text, 3 )
						if id:
							if util.isInt(id):
								if self.assets['config']['single_channel'].get(chan):
									if self.assets['config']['single_channel'][chan].get('auto_msgs'):
										try:
											_tmp = self.assets['config']['single_channel'][chan]['auto_msgs']['messages'][ int(id) ]
											if len(self.assets['config']['single_channel'][chan]['auto_msgs']['messages']) > 1:
												self.assets['config']['single_channel'][chan]['auto_msgs']['messages'].pop( int(id) )
											else:
												self.assets['config']['single_channel'][chan].pop('auto_msgs')
												util.AutoMessages(self, False)
												if len(self.assets['config']['single_channel'][chan]) == 0:
													self.assets['config']['single_channel'].pop(chan)
											self.message(_("10>1 \"%s\" 4deleted from the list of auto messages") % _tmp, chan)
										except Exception, e:
											print str(e)
											self.message(_("> %s is unknown message ID") % id, chan)
									else:
										self.message(_("10> 4This channel is not configured to use this command!"), chan)
								else:
									self.message(_("10> 4This channel is not configured to use this command!"), chan)
							else:
								self.message(_("> %s is unknown message ID") % id, chan)
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <id>" % (prx, cmd, place, param, value)), chan)
					elif value == 'remove':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get('auto_msgs'):
								self.assets['config']['single_channel'][chan].pop('auto_msgs')
								if len(self.assets['config']['single_channel'][chan]) == 0:
									self.assets['config']['single_channel'].pop(chan)
								self.message(_("10>1 \"%s\" 4deleted from the list of auto messages") % chan, chan)
							else:
								self.message(_("10> 4This channel is not configured to use this command!"), chan)
						else:
							self.message(_("10> 4This channel is not configured to use this command!"), chan)
					elif value == 'turn':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get('auto_msgs'):
								if self.assets['config']['single_channel'][chan]['auto_msgs']['active']:
									self.assets['config']['single_channel'][chan]['auto_msgs']['active'] = False
								else:
									self.assets['config']['single_channel'][chan]['auto_msgs']['active'] = True
								
								self.message(_("10>14 Auto-messages are now turned %s, in1 %s") % ( _("on") if self.assets['config']['single_channel'][chan]['auto_msgs']['active'] == True else _("off"), chan ), chan)
							else:
								self.message(_("10> 4This channel is not configured to use this command!"), chan)
						else:
							self.message(_("10> 4This channel is not configured to use this command!"), chan)
					elif value == 'list':
						if self.assets['config']['single_channel'].get(chan):
							if self.assets['config']['single_channel'][chan].get('auto_msgs'):
								buffer = ""
								i = 0
								for msg in self.assets['config']['single_channel'][chan]['auto_msgs']['messages']:
									buffer += "[%i] %s..., " % ( i, msg[:15] )
									i += 1
								self.message(_("10> 14Auto messages with13:1 %s 14and on a loop of 25min.") % (buffer[:len(buffer)-2]), chan)
							else:
								self.message(_("10> 4This channel is not configured to use this command!"), chan)
						else:
							self.message(_("10> 4This channel is not configured to use this command!"), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <set/del/remove/turn/list>" % (prx, cmd, place, param)), chan)
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s <join/part/welcome/automessages/flood>" % (prx, cmd, place)), chan)
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
						elif self.assets['config']['single_channel'].get(chan) and self.assets['config']['single_channel'][chan].get( 'custom_command' ) and self.assets['config']['single_channel'][chan]['custom_command'].get( value ):
							if self.assets['config']['single_channel'][chan]['custom_command'][ value ]['active'] == True:
								self.assets['config']['single_channel'][chan]['custom_command'][ value ]['active'] = False
								self.message( _("> \"%s\" 4are now ignore on1 %s") % ( value, chan ), chan )
							else:
								self.assets['config']['single_channel'][chan]['custom_command'][ value ]['active'] = True
								self.message( _("> \"%s\" 4are now listened on1 %s") % ( value, chan ), chan )
						else:
							self.message( _("> %s 4is a unknow command to me") % value, chan )
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command>" % (prx, cmd, place, param)), chan)
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
								self.message( _("> %s 4is a unknow command to me") % value, chan )
						else:
							self.message(_(">4 This is not allowed."), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command>" % (prx, cmd, place, param)), chan)
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
								self.message( _("> %s 4is a unknow command to me") % value, chan )
						else:
							self.message(_(">4 This is not allowed."), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command>" % (prx, cmd, place, param)), chan)
				elif param == 'alias':
					if value:
						if self.assets['commands'].get( value ):
							_alias = " ".join(text.split(' ')[3:])
							if len(_alias) > 0:
								if self.assets['commands'].get( _alias ):
									self.message(_("> \"%s\" 4already exists!") % _alias, chan)
								else:
									if _alias.lower() in self.assets['commands'][ value ]['alias']:
										self.assets['commands'][ value ]['alias'].pop( self.assets['commands'][ value ]['alias'].index(_alias.lower()) )
										self.message( _("> \"%s%s\" 4is now removed from bot") % ( prx, _alias ), chan )
									else:
										if util.isCmdAlias( self, _alias ) == None:
											self.assets['commands'][ value ]['alias'].append( _alias.lower() )
											self.message(_("> \"%s%s\" 10new command created") % (prx,_alias), chan)
										else:
											self.message(_("> \"%s\" 4already exists!") % _alias, chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <alias>" % (prx, cmd, place, param, value)), chan)
						else:
							self.message( _("> %s 4is a unknow command to me") % value, chan )
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command> <alias>" % (prx, cmd, place, param)), chan)
				elif param == 'new':
					if value:
						_message = " ".join(text.split(' ')[3:])
						if self.assets['commands'].get( value ):
							self.message(_("> \"%s\" 4already exists!") % value, chan)
						elif self.assets['config']['single_channel'].get( chan ) and self.assets['config']['single_channel'][chan].get( 'custom_command' ) and self.assets['config']['single_channel'][chan]['custom_command'].get( value ):
							self.message(_("> \"%s\" 4already exists!") % value, chan)
						else:
							if len( _message ) > 0:
								if self.assets['config']['single_channel'].get( chan ):
									if self.assets['config']['single_channel'][ chan ].get( 'custom_command' ):
										self.assets['config']['single_channel'][ chan ]['custom_command'].setdefault( value.lower(), {"active": True, "message": _message} )
									else:
										self.assets['config']['single_channel'][ chan ].setdefault( 'custom_command', { value.lower(): {"active": True, "message": _message} } )
								else:
									self.assets['config']['single_channel'].setdefault( chan, { 'custom_command': {value.lower(): {"active": True, "message": _message}} } )
								self.message(_("> \"%s%s\" 10new command created") % (prx,value), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s %s <message>" % (prx, cmd, place, param, value)), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command> <message>" % (prx, cmd, place, param)), chan)
				elif param == 'del':
					if value:
						if self.assets['config']['single_channel'].get( chan ):
							if self.assets['config']['single_channel'][chan].get( 'custom_command' ) and self.assets['config']['single_channel'][chan]['custom_command'].get( value ):
								if len( self.assets['config']['single_channel'][chan]['custom_command'] ) > 1:
									self.assets['config']['single_channel'][chan]['custom_command'].pop( value )
								else:
									self.assets['config']['single_channel'][chan].pop( 'custom_command' )
								if len(self.assets['config']['single_channel'][chan]) == 0:
									self.assets['config']['single_channel'].pop( chan )
								self.message( _("> \"%s%s\" 4is now removed from bot") % ( prx, value ), chan )
							else:
								self.message( _("> %s 4is a unknow command to me") % value, chan )
						else:
							self.message(_("10> 4This channel is not configured to use this command!"), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s %s <command>" % (prx, cmd, place, param)), chan)
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s <turn/ignore/formod/new/del/alias>" % (prx, cmd, place)), chan)
			else:
				self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <osu/stats/commands/channel>" % (prx, cmd)), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <osu/stats/commands/channel>" % (prx, cmd)), chan)
	
	else:
		onCommand(self, chan, user, cmd, text)
	
def onCommand(self, chan, user, cmd, text):
	_ = util.GetLangStrings( self, strings, user, chan )
	
	prx = self.assets['config']['prefix']
	
	if cmd == 'commands':
		buffer = ""
		is_mod = False
		if user in self.assets['config']['mods']: is_mod = True
		for cmds in self.assets['commands']:
			if self.assets['commands'][ cmds ]['active'] != False and chan not in self.assets['commands'][ cmds ]['ignore']:
				if self.assets['commands'][ cmds ]['mod'] and is_mod == False: pass
				else: buffer += "%s%s, " % (prx + cmds, "" if len(self.assets['commands'][ cmds ]['alias']) <= 0 else "(%s)" % (", ".join(self.assets['commands'][ cmds ]['alias'])))
		if self.assets['config']['single_channel'].get(chan) and self.assets['config']['single_channel'][chan].get( 'custom_command' ):
			for cmds in self.assets['config']['single_channel'][chan]['custom_command']:
				if self.assets['config']['single_channel'][chan]['custom_command'][ cmds ]['active'] != False:
					buffer += prx + cmds + ", "
		if len( self.assets['commands'] ) > 0: self.message('>> %s' % buffer[:len(buffer)-2], chan)
		else: self.message( _('>> No Commands Found.'), chan)
		
	elif cmd == 'setlang':
		if len(text) > 0:
			if text in LANG:
				if user in self.assets['config']['use_langs'][text]:
					self.message(_("10>4 You are already using this language"), chan)
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
				self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s" % (prx, cmd, ", ".join(LANG)) ), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s" % (prx, cmd, ", ".join(LANG)) ), chan)
	
	elif cmd == 'bot':
		i = util.getinfo()
		self.message(_('11>1 %s v%s by NT5 3-1 Python %s 3-1 System6:1 %s %s %s 3-1 Uptime6:1 %s 3-1 Channels6:1 %i 3-1 Stats6:1 (Users6:1 %s Channels6:1 %s Words6:1 %s Links6:1 %s) 3-1 Quotes6:1 %s 3-1 Aways6:1 %s') % ( self.nick, self.version, sys.version.splitlines()[0], i[0], i[2], i[4], util.getDHMS( int( int( time.time() ) - self.uptime['server'] )), len( self.channels ), util.group(len(self.assets['stats']['users'])), util.group(len(self.assets['stats']['channels'])), util.group(len(self.assets['stats']['words'])), util.group(len(self.assets['stats']['links'])), util.group(len(self.assets['quotes'])), util.group(len(self.assets['aways']))), chan )
		
	elif cmd == 'uptime':
		self.message( _('11>1 %s Server Uptime: %s - Script Uptime: %s') % (self.nick, util.getDHMS( int( int( time.time() ) - self.uptime['server'] )), util.getDHMS( int( int( time.time() ) - self.uptime['script'] ))), chan)
	
	elif cmd == '8ball':
		if len(text) > 0:
			bases = [_("It is certain"), _("It is decidedly so"), _("Without a doubt"), _("Yes definitely"), _("You may rely on it"), _("As I see it, yes"), _("Most likely"), _("Outlook good"), _("Yes"), _("Signs point to yes"), _("Reply hazy try again"), _("Ask again later"), _("Better not tell you now"), _("Cannot predict now"), _("Concentrate and ask again"), _("Don't count on it"), _("My reply is no"), _("My sources say no"), _("Outlook not so good"), _("Very doubtful")]
			self.message("> 10%s" % random.choice(bases), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s < ...? >" % (prx, cmd) ), chan)
			
	elif cmd == 'stats':
		u = None
		if len( text ) > 0: q = text
		else: q = user
		
		if self.assets['stats']['users'].get( q ):
			u = self.assets['stats']['users'][ q ]
		elif self.assets['stats']['channels'].get( q ):
			u = self.assets['stats']['channels'][ q ]
			
		if u:
			Time = int( time.time() ) - u['seen']
			self.message( _("> %s 10Stats ago13:1 %s 3-10 Activity points13:1 %s 3-10 Letters13:1 %s 10Words13:1 %s 10Lines13:1 %s 10Smiles13:1 %s 3-1 \"%s...\"") % ( q, util.getDHMS( Time ) if Time >= 2 else _("now"), util.group( u['timeline']['ap'] ), util.group( int( u['letters'] ) ), util.group( int( u['words'] ) ), util.group( int( u['lines'] ) ), util.group( int( u['smiles'] ) ), u['quote'][:50] ), chan )
		else:
			self.message( _("> %s 4is a unknown name to me") % q, chan )
			
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
			self.message( _("10>4 You are not set away"), chan )
			
	
	elif cmd == 'afk':
		if len( text ) > 0:
			if self.assets['aways'].get( text ):
				x = self.assets['aways'].get( text )
				self.message( _(">10 %s 3- 14reason13:1 %s 3- 14Time13:1 %s") % ( text, x['reason'], util.getDHMS( int( int( time.time() ) - x['time'] )) ), chan )
			elif text.lower() == "@all":
				if len( self.assets['aways'] ) > 0:
					util._cmdLimiter( self, 'b', chan, cmd )
						
					for x in self.assets['aways']:
						self.message( _(">10 %s 3- 14reason13:1 %s 3- 14Time13:1 %s") % ( x, self.assets['aways'][ x ]['reason'], util.getDHMS( int( int( time.time() ) - self.assets['aways'][ x ]['time'] )) ), chan )
					time.sleep(2)
					util._cmdLimiter( self, 'u', chan, cmd )
					
				else:
					self.message( _(">14 Nobody in this channel is absent."), chan )
			else:
				self.message( _("> %s 4is a unknown name to me") % text, chan )
		else:
			if len( self.assets['aways'] ) > 0:
				c_channel = 0
				for x in self.names[ chan ]:
					if self.assets['aways'].get( x ):
						c_channel += 1
						self.message( _(">10 %s 3- 14reason13:1 %s 3- 14Time13:1 %s") % ( x, self.assets['aways'][ x ]['reason'], util.getDHMS( int( int( time.time() ) - self.assets['aways'][ x ]['time'] )) ), chan )
				if c_channel == 0:
					self.message( _(">14 Nobody in this channel is absent."), chan )
			else:
				self.message( _(">14 Nobody in this channel is absent."), chan )
	
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
				self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <add/del/last/id>" % (prx, cmd) ), chan)
		else:
			if len( self.assets['quotes'] ) == 0:
				self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <add/del/last/id>" % (prx, cmd) ), chan)
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
							urllib2.socket.setdefaulttimeout(15)
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
								except Exception, e:
									print e
									self.message(_("4Error occurred :("), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <game/title> <parameter>" % (prx, cmd) ), chan)
						elif param == 'title':
							if util.gettext(text, 1):
								title = text[len(param)+1:]
								try:
									_dotwitch(urllib2.quote(title.encode('utf-8')), 'status')
									self.message(_("10> 14Title set to13:1 %s") % title, chan)
								except Exception, e:
									print e
									self.message(_("4Error occurred :("), chan)
							else:
								self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <game/title> <parameter>" % (prx, cmd) ), chan)
						else:
							self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <game/title> <parameter>" % (prx, cmd) ), chan)
					else:
						self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <game/title> <parameter>" % (prx, cmd) ), chan)
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
						_map = util.getOsuLink( text )
						if _map:
							util._cmdLimiter( self, 'b', chan, cmd )
							def _getstats(stats):
								format = "[%s%s]"
								return format % ( "*"*int(float(stats)), "-"*(10-int(float(stats))) )
							try:
								q = util.json_request( self.assets['api']['osu']['request'][1] % ( self.assets['api']['osu']['url'], self.assets['api']['osu']['key'], "=".join(_map) ), {} )[0]
								_msg = "%s - %s %s (%s) mapped by: %s - BPM: %s - %s (Stars: %.2f - AR: %.2f - CS: %.2f - OD: %.2f - HP: %.2f) - %s" % ( q['title'], q['artist'], "("+q['source'].decode("unicode-escape")+")" if len(q['source']) > 0 else "", util.getDHMS(int(q['total_length'])), q['creator'], q['bpm'], _getstats(q['difficultyrating']), float(q['difficultyrating']), float(q['diff_approach']), float(q['diff_size']), float(q['diff_overall']), float(q['diff_drain']), "http://osu.ppy.sh/"+"/".join(_map))
								for _user in self.assets['config']['single_channel'][chan]['osu_req']['users']:
									self._banchonet.message("[REQUEST] [%s]: %s" % (user, _msg), _user )
									time.sleep(1)
								self.message(_("10> 14Your request was sent13:1 \"%s\" 14to13:1 %s") % (_msg, ", ".join(self.assets['config']['single_channel'][chan]['osu_req']['users'])), chan)
							except:
								self.message(_("10> 4Invalid link!"), chan)
							time.sleep(1.5)
							util._cmdLimiter( self, 'u', chan, cmd )
						else:
							self.message(_("10> 4Invalid link!"), chan)
					else:
						self.message(_("10> 4The requests are turned off."), chan)
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <osu link>" % (prx, cmd) ), chan)
			else:
				self.message(_("10> 4This channel is not configured to use this command!"), chan)
		else:
			self.message(_("10> 4This channel is not configured to use this command!"), chan)
	
	elif cmd == 'mc':
		if len( text ) > 0:
			def _doQuery( ip, port = 25565):
				try:
					q  = MinecraftQuery(ip, int(port))
					info = q.get_rules()
					self.message(_( "10>1 %s 3- 10Players6:1 [%i/%i] 3- 10Map6:1 %s" ) % ( util.NoMCColors( info['motd'] ), info['numplayers'], info['maxplayers'], info['map'] ), chan )
					if len( info['players'] ) > 0 and  len( info['players'] ) <= 30:
						self.message( ", ".join( info['players'] ), chan )
				except Exception, e:
					self.message( _("10>4 Unknown server"), chan )
			ip = util.gettext( text, 0, ':' )
			port = util.gettext( text, 1, ':' )
			if ip and port:
				_doQuery( ip, port )
			else:
				_doQuery( text )
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <IP:PORT>" % (prx, cmd) ), chan)
	
	elif cmd == 'vcmp':
		if len( text ) > 0:
			def _doQuery( ip, port ):
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
						self.message( _("10>1 %s 3- 10Server6:1 %s 10IP6:1 %s:%s 10Gamemode6:1 %s 10Players6:1 [%i/%i] %s") % ( util.gettext( text, 0 ), info['hostname'].decode('utf-8'), str(ip), str(port), info['gamemode'].decode('utf-8'), info['players'], info['maxplayers'], _('4Close') if info['password'] == 1 else _('3Open')), chan )
						if len( player_string ) > 0:
							self.message( player_string[:len(player_string)-2], chan )
					except Exception, e:
						self.message( _("10>4 Unknown server"), chan )
				q.close()
				
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
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s add <server> <IP:PORT>" % (prx, cmd)), chan)
			elif util.gettext( text, 0 ) == 'del' and user in self.assets['config']['mods']:
				if util.gettext( text,1 ):
					if self.assets['config']['vcmp_servers'].get( util.gettext( text, 1 ) ):
						self.assets['config']['vcmp_servers'].pop( util.gettext( text, 1 ) )
						self.message( _("10>1 \"%s\" 4is now removed from server list") % util.gettext( text, 1 ), chan )
					else:
						self.message( _("10>1 \"%s\" 4is a unknown server to me") % util.gettext( text, 1 ), chan )
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s del <server>" % (prx, cmd)), chan)
			elif util.gettext( text, 0 ) == 'list':
				if len( self.assets['config']['vcmp_servers'] ) > 0:
					self.message( "%s%s <%s>" % ( prx, cmd, ", ".join(self.assets['config']['vcmp_servers']) ), chan )
				else:
					self.message( _("10>4 Without servers."), chan )
			elif util.gettext( text, 0 ) == 'master':
				util._cmdLimiter( self, 'b', chan, cmd )
					
				_masterlist = {}
				_servers = []
				_progress = 0
				_timeout =  0.5
				_timeexec = int( time.time() )
				try: _masterlist = util.uniq( util.web_request( "http://vicecitymultiplayer.com/servers.php" ).split( "\n" ) )
				except Exception, e: self.message( _("> 4Can't connect to master list %s") % e, chan )

				self.message( _("10>1 %i 14Servers on master list, estimated time13:1 %s") % (len( _masterlist ), util.getDHMS(int(len( _masterlist ) * _timeout))), chan )
				self.message( "10"+"~-"[:6]*35, chan )

				for server in _masterlist:
					try:
						_progress += 1
						if len( server.split(":") ) > 1:
							query = vcmpQuery( None, str( server.split(":")[0] ), int( server.split(":")[1] ), timeout = _timeout )
							if query:
								try:
									query.connect()
									info = query.getInfo()
									_servers.append( {'hostname': info['hostname'], 'gamemode': info['gamemode'], 'players': info['players'], 'maxplayers': info['maxplayers'], 'ip': server} )
									self.message(  "10> 13[{progress}%]6 {hostname} {gamemode} 13[{players}/{maxplayers}]10 {ip}".format( hostname = info['hostname'].decode('utf-8'), gamemode = info['gamemode'].decode('utf-8'), players = info['players'], maxplayers = info['maxplayers'], ip = server, progress = ( 100 * _progress / len( _masterlist ) ) ), chan, show = False )
									query.close()
								except Exception, e: pass
					except: pass
				self.message( "10"+"~-"[:6]*35, chan )
				self.message( _("10> 13[100%%]14 %i Valid servers 3-1 %s") % (len( _servers ), util.getDHMS( int( time.time() ) - _timeexec)), chan )
				util._cmdLimiter( self, 'u', chan, cmd )
						
			elif self.assets['config']['vcmp_servers'].get( util.gettext( text, 0 ) ):
				ip = self.assets['config']['vcmp_servers'][ util.gettext( text, 0 ) ]['ip']
				port = self.assets['config']['vcmp_servers'][ util.gettext( text, 0 ) ]['port']
				_doQuery( ip, port )
			else:
				ip = util.gettext( text, 0, ':' )
				port = util.gettext( text, 1, ':' )
				if ip and port:
					_doQuery( ip, port )
				else:
					self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s" % (prx, cmd, '<master/list/add/del/IP:PORT/server>' if user in self.assets['config']['mods'] else '<master/list/IP:PORT/server>' ) ), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s %s" % (prx, cmd, '<master/list/add/del/IP:PORT/server>' if user in self.assets['config']['mods'] else '<master/list/IP:PORT/server>' ) ), chan)
	
	elif cmd == 'weather':
		if len( text ) > 0:
			try:
				q = util.json_request( self.assets['api']['weather']['request'] % ( self.assets['api']['weather']['url'], urllib2.quote( text.encode("utf-8") ) ), {} )
				self.message( _(u"11>1 %s %s 3-5 %s 3- 14Coord13:1 %s, %s 3- 14Temp13:1 %s14c 3- 14Humidity13:1 %s%% 3- 14Pressure13:1 %s14hPa 3- 14Wind13:1 %s14mps") % ( q['name'], q['sys']['country'], q['weather'][0]['description'], str(q['coord']['lat']), str(q['coord']['lon']), str( ( int( q['main']['temp'] ) - 273.15 ) * 1.0000 ), str(q['main']['humidity']), util.group( int( q['main']['pressure'] ) ), str(q['wind']['speed']) ), chan )
			except Exception, e:
				self.message( _("4Search failed"), chan )
		else:
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
			
	elif cmd == 'translate':
		if len( text ) > 0:
			util._cmdLimiter( self, 'b', chan, cmd )
			_langs = {"af": "Afrikaans","sq": "Albanian","ar": "Arabic","az": "Azerbaijani","eu": "Basque","bn": "Bengali","be": "Belarusian","bg": "Bulgarian","ca": "Catalan","zh-CN": "Chinese Simplified","zh-TW": "Chinese Traditional","hr": "Croatian","cs": "Czech","da": "Danish","nl": "Dutch","en": "English","eo": "Esperanto","et": "Estonian","tl": "Filipino","fi": "Finnish","fr": "French","gl": "Galician","ka": "Georgian","de": "German","el": "Greek","gu": "Gujarati","ht": "Haitian Creole","iw": "Hebrew","hi": "Hindi","hu": "Hungarian","is": "Icelandic","id": "Indonesian","ga": "Irish","it": "Italian","ja": "Japanese","kn": "Kannada","ko": "Korean","la": "Latin","lv": "Latvian","lt": "Lithuanian","mk": "Macedonian","ms": "Malay","mt": "Maltese","no": "Norwegian","fa": "Persian","pl": "Polish","pt": "Portuguese","ro": "Romanian","ru": "Russian","sr": "Serbian","sk": "Slovak","sl": "Slovenian","es": "Spanish","sw": "Swahili","sv": "Swedish","ta": "Tamil","te": "Telugu","th": "Thai","tr": "Turkish","uk": "Ukrainian","ur": "Urdu","vi": "Vietnamese","cy": "Welsh","yi": "Yiddish"}

			regex = re.compile("({langs}\.*?):({langs}\.*?) (.+)".format( langs = "|".join(_langs) ), re.MULTILINE).findall(text)
			if len(regex) > 0:
				_from = regex[0][0]
				_to = regex[0][1]
				_text = regex[0][2]
				result, code, string = util.get_google_translate( _text, _to, _from )
				if result:
					self.message( _("13> 14Translate from1 %s13:1 14to13:1 %s14 \"%s\".") % (_langs[_from], _langs[_to], string), chan )
				else:
					self.message( _("13> 4Can't translate text1 %s") % (string), chan )
			elif text.lower() == "@list":
				b = ""
				for lang in _langs:
					b += "%s13:1%s, " % ( _langs[lang], lang )
				self.message( _("13> 14Available languages13:1 %s") % b[:len(b)-2], chan )
			else:
				self.message( _("13> 4Can't translate text1 Invalid language"), chan )
			util._cmdLimiter( self, 'u', chan, cmd )
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s [@list] <en,es..>:<es,en..> <text>" % (prx, cmd)), chan)
	
	elif cmd == 'facebook':
		if len( text ) > 0:
			search = str( urllib2.quote( text.encode("utf-8").replace( ' ', '.' ) ) )
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
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
			
	elif cmd == 'mal':
		if len(text) > 0:
			def get_mal_user( user ):
				regexs = {
					"user": "<div .*?>(.*?) Details</div>",
					"lastonline": "<td .*?>Last Online</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"gender": "<tr>\s.*\s<td .*?>Gender</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"birthday": "<td .*?>Birthday</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"location": "<tr>\s.*\s<td .*?>Location</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"website": "<td .*?>Website</td>\s.*\s<td><a href=\"(.*?)\" target=\"_blank\">.*?</a></td>\s.*\s</tr>",
					"joindate": "<tr>\s.*\s<td .*?>Join Date</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"rank": "<tr>\s.*\s<td .*?>Access Rank</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"viewsanimes": "<tr>\s.*\s<td .*?>Anime List Views</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"viewsmangas": "<tr>\s.*\s<td .*?>Manga List Views</td>\s.*\s<td>(.*?)</td>\s.*\s</tr>",
					"listupdates": "<a href=\"(.*?)\">(.*?)</a> <a href=\".*?\" title=\".*?\" class=\".*?\">add</a> \s.*\s<div class=\"spaceit_pad\">(.*?)</div>\s.*\s<div class=\"lightLink\">(.*?)</div>",
					"mang_anim_stats": "<td width=\".*?\"><span class=\".*?\">(.*?)</span></td>\s.*\s<td align=\".*?\">(.*?)</td>"
				}
				
				data = util.web_request( self.assets['api']['myanimelist']['request'] % ( self.assets['api']['myanimelist']['url'], user ), headers = { 'User-Agent' : self.assets['api']['myanimelist']['agent'] } )
				
				_re = {}
				
				for k, v in regexs.items():
					regex = regex = re.compile( v ,re.UNICODE)
					par_ = regex.findall( data )
					if par_:
						_re.setdefault( k, par_)
					else:
						_re.setdefault( k, ["Unknown"])
						
				if len( _re ) > 0:
					return _re
				else:
					return None
			
			mal = get_mal_user( urllib2.quote(text.encode('utf-8')) )
			if mal:
				try:
					list_updates = []
					mang_anim_stats = { "manga": [], "anime": [] }
					if mal['listupdates'] != ["Unknown"]:
						for ani in mal['listupdates']:
							list_updates.append( "%s6: %s (12%s%s) %s" % (ani[2], ani[1].decode("unicode-escape"), self.assets['api']['myanimelist']['url'], ani[0].decode("unicode-escape"), ani[3] ) )
					else:
						list_updates.append( "Unknown" )
						
					if mal['mang_anim_stats'] != ["Unknown"]:
						_count = 0
						for val in mal['mang_anim_stats']:
							if _count <= 5:
								mang_anim_stats['anime'].append( "6: ".join( val ) )
							else:
								mang_anim_stats['manga'].append( "6: ".join( val ) )
							_count += 1
					else:
						mang_anim_stats = { "manga": ["Unknown"], "anime": ["Unknown"] }
						
					self.message( _("> %s Details 3- 2Last Online6:1 %s 3- 2Gender6:1 %s 3- 2Birthday6:1 %s 3- 2Location6:1 %s 3- 2Website6:1 12%s 3- 2Join Date6:1 %s 3- 2Rank6:1 %s 3- 2Anime List Views6:1 %s 3- 2Manga List Views6:1 %s 3- 2Last List Updates6:1 %s 3- 2Anime Stats6:1 (%s) 3- 2Manga Stats6:1 (%s)") % (mal['user'][0], mal['lastonline'][0], mal['gender'][0], mal['birthday'][0], mal['location'][0], mal['website'][0], mal['joindate'][0], mal['rank'][0], mal['viewsanimes'][0], mal['viewsmangas'][0], ", ".join(list_updates), " - ".join( mang_anim_stats['anime'] ), " - ".join( mang_anim_stats['manga'] ) ), chan )
				
				except Exception, e:
					self.message(_("4Unknown User"), chan)
			else:
				self.message(_("4Unknown User"), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "<myanimelist user>" ), chan )
	
	elif cmd == 'osu':
		if len(text) > 0:
			regex = re.compile("m:(standar|taiko|ctb|mania\.*?) (.+)", re.MULTILINE).findall(text)
			if len(regex) > 0:
				try:
					_user = regex[0][1]
					mode = regex[0][0]
				except:
					mode = 'standar'
					_user = text
			else:
				mode = 'standar'
				_user = text
			if mode == 'taiko': mode = 1
			elif mode == 'ctb': mode = 2
			elif mode == 'mania': mode = 3
			else: mode = 0
			try:
				q = util.json_request( self.assets['api']['osu']['request'][0] % ( self.assets['api']['osu']['url'], self.assets['api']['osu']['key'], mode, urllib2.quote( _user ) ), {} )[0]
				self.message( _("> 6%s 3- 14Country6: 1%s 3- 14Play Count6:1 %s 3- 14Ranked Score6:1 %s 3- 14Total Score6:1 %s 3- 14Level6:1 %d 3- 14Accuracy6:1 %0.f%% 3- 14PP6:1 %0.f 3- 14Rank6:1 #%s") % ( q['username'], q['country'], util.group( int(q['playcount']) ), util.group( int(q['ranked_score']) ), util.group( int(q['total_score']) ), float( q['level'] ), float( q['accuracy']) , float( q['pp_raw'] ), util.group( int( q['pp_rank']) ) ), chan )
			except Exception, e:
				self.message(_("4Unknown User"), chan)
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s [m:<ctb, taiko, mania, standar>] <user name>" % (prx, cmd) ), chan)
	
	elif cmd == 'animeflv':
		if len( text ) > 0:
			util._cmdLimiter( self, 'b', chan, cmd )
			try:
			
				def gender_split( string ):
					regex = re.compile("<a href=\".*?\">(.*?)</a>",re.UNICODE)
					find = regex.findall( string )
					if find: return ", ".join(find)
					else: return None
					
				page = util.web_request( self.assets['api']['animeflv']['request'] % ( self.assets['api']['animeflv']['url'], urllib2.quote( text.encode("utf-8") ) ) )
				regex = re.compile("<a href=\"(.*?)\" title=\"(.*?)\" class=\"titulo\">.*?\</a>\n<div class=\"generos_links\">(.*?)</div>\n<div class=\"sinopsis\">(.*?)(?:</div>|\n</div>)",re.UNICODE)
				regexf = regex.findall( page )
				if len( regexf ) > 0:
					_count = 0
					for anim in regexf:
						_count += 1
						if _count <= 5:
							anime = { 'link': anim[0], 'title': anim[1], 'gender': gender_split( anim[2] ), 'synopsis': anim[3] }
					
							self.message( _("> 10Title6:1 %s 3- 10Link6: 12%s%s 3- 10Gender6:1 %s 3- 10Synopsis6:1 %s") % ( util.NoHTML(anime['title'].decode('utf-8')), self.assets['api']['animeflv']['url'][:-1], util.NoHTML(anime['link'].decode('utf-8')), util.NoHTML(anime['gender']), util.NoHTML(anime['synopsis'].decode('utf-8')) ), chan )
				else:
					self.message( _("4Search Failed"), chan )
			except Exception, e:
				self.message( _("4Search Failed"), chan )
			util._cmdLimiter( self, 'u', chan, cmd )
		else:
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
			
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
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
	
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
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
			
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
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
	
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
	
	elif cmd == 'google':
		if len(text) > 0:
			util._cmdLimiter( self, 'b', chan, cmd )
			try:
				_gs = util.get_google_search( text )
				if len( _gs ) > 0:
					for gs in _gs:
						self.message( _('2G4o7o2g3l4e 10Search: 14%s 3- 14%s 3- 12%s') % ( gs['title'], gs['description'], gs['link'] ), chan )
				else:
					self.message( _("4Search failed"), chan )
			except Exception, e:
				self.message( _("4Search failed"), chan )
			util._cmdLimiter( self, 'u', chan, cmd )
		else:
			self.message(_("7Syntax:1 {syntax} <search>").format( syntax = "%s%s" % (prx, cmd) ), chan)
	
	elif cmd == 'talk':
		if len(text) > 0:
			def CreateSessionBot():
				from res.chatterbotapi import ChatterBotFactory
				factory = ChatterBotFactory()
				bot = factory.create( self.cleverbot['type'] )
				return bot.create_session()
				
			if ( self.cleverbot['users'].get( user ) == None ):
				self.cleverbot['users'].setdefault( user, { "core": CreateSessionBot(), "last_use": 0, "waiting": False } )
				self.message(_("10>1 %s is now talking with %s") % ( user, self.nick ), chan)
				if len( self.cleverbot['users'] ) > 5:
					for x in list(self.cleverbot['users']):
						if ( int( time.time() ) - self.cleverbot['users'][ x ]['last_use'] ) >= 120:
							del self.cleverbot['users'][ x ]
			
			if self.cleverbot['users'][ user ]['waiting'] == True:
				if ( int( time.time() ) - self.cleverbot['users'][ user ]['last_use'] ) >= 60:
					self.message(_("10>1 %s 4response timed out :(!, try again!") % user, chan)
					del self.cleverbot['users'][ user ]
				else:
					self.message( _("10>1 %s 4wait for your answer!") % user, chan )
			elif ( int( time.time() ) - self.cleverbot['users'][ user ]['last_use'] ) <= 2:
				self.message( _("10>1 %s - Wait one moment before talk") % user, chan )
			else:
				try:
					if ( text.lower() == "stop" ):
						self.message(_("10>1 %s, see you later!") % ( user ), chan)
						del self.cleverbot['users'][ user ]
					else:
						self.cleverbot['users'][ user ]['waiting'] = True
						self.cleverbot['users'][ user ]['last_use'] = int( time.time() )
						response = self.cleverbot['users'][ user ]['core'].think( text.encode('utf-8') )
						self.message("11>3 %s 1->12 %s:1 %s" % ( self.nick, user, util.NoHTML(response) ), chan)
						self.cleverbot['users'][ user ]['waiting'] = False
				except Exception, e:
					self.message( _("10>4 Talking Fail. - %s") % str( e ), chan )
					del self.cleverbot['users'][ user ]
		else:
			self.message(_("7Syntax:1 {syntax}").format( syntax = "%s%s <text/stop>" % (prx, cmd) ), chan)
	
	else:
		if self.assets['config']['single_channel'].get(chan) and self.assets['config']['single_channel'][chan].get( 'custom_command' ) and self.assets['config']['single_channel'][chan]['custom_command'].get( cmd ):
			try:
				_message = self.assets['config']['single_channel'][chan]['custom_command'][cmd]['message'].format( user = user, chan = chan, me = self.nick, text = text, cmd = cmd, prx = prx, color = "\u0003", underline = "\u001f", bold = "\u0002", italic = "\u001d" )
				self.message( _message.decode("unicode-escape"), chan )
			except:
				self.message( self.assets['config']['single_channel'][chan]['custom_command'][cmd]['message'], chan )

