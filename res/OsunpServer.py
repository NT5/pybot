#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer, urllib2
from encryp import Encryp
cryp = Encryp()

class osunp_handler_class(BaseHTTPRequestHandler):
	def log_message(self, format, *args):
		return
			
	def _set_headers(self, code = 200):
		self.send_response(code)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def _parse_post(self, data):
		try:
			post_body = data.split('&')
			vars = {}
			for v in post_body:
				try:
					tmp = v.split('=')
					vars.setdefault(tmp[0], tmp[1])
				except: pass
			return vars
		except: return None
	
	def do_GET(self):
		self._set_headers(400)
		self.wfile.write("<html><body><h1>This is not allowed!</h1></body></html>")

	def do_HEAD(self):
		self._set_headers()

	def do_POST(self):
		if self.path == '/osupost':
			self._set_headers()		
			content_len = int(self.headers.getheader('content-length'))
			post_body = self.rfile.read(content_len)
			self.wfile.write("<html><body>")
			try:
				vars = self._parse_post(post_body)
				user = cryp.decode(vars['key'])
				messages = []
				if vars["mapName"] != "NoMap": messages.append("%s" % urllib2.unquote(vars['mapName']).replace('+', ' '))
				if vars["mapSetID"] != "-1": messages.append("Map: http://osu.ppy.sh/s/%s" % vars['mapSetID'])
				if len(messages) > 0:
					#Send messages to bots
					for loc in SenderIns.senders:
						if loc.assets['config']['osu_np'].get(user):
							for chan in loc.assets['config']['osu_np'][user]:
								loc.message( "13[Osu!] [10%s13]14 %s" % (user, " - ".join(messages)), chan, show = False )
							self.wfile.write("<h1>[%s] Accepted</h1>" % loc.nick)
						else:
							self.wfile.write("<h1>[%s] Access denied!</h1>" % loc.nick)
			except Exception, e:
				self.wfile.write("<h1>Exception ocurred %s</h1>" % str(e))
			self.wfile.write("</body></html>")
		
		elif self.path == '/osunp':
			self._set_headers()		
			content_len = int(self.headers.getheader('content-length'))
			post_body = self.rfile.read(content_len)
			vars = self._parse_post(post_body)
			self.wfile.write("<html><body>")
			if vars:
				try:
					messages = []
					user = cryp.decode(vars['key'])
					if vars.get("primary"): messages.append("%s" % urllib2.unquote(vars['primary']).replace('+', ' '))
					if vars.get("secondary"): messages.append("%s" % urllib2.unquote(vars['secondary']).replace('+', ' '))
					if len(messages) > 0:
						#Send messages to bots
						for loc in SenderIns.senders:
							if loc.assets['config']['osu_np'].get(user):
								for chan in loc.assets['config']['osu_np'][user]:
									loc.message( "13[Osu!] [10%s13]14 %s" % (user, " - ".join(messages)), chan, False )
								self.wfile.write("<h1>[%s] Accepted</h1>" % loc.nick)
							else:
								self.wfile.write("<h1>[%s] Access denied!</h1>" % loc.nick)
					else: self.wfile.write("<h1>No message to send!</h1>")
				except Exception, e: self.wfile.write("<h1>Exception ocurred %s</h1>" % str(e))
				self.wfile.write("</body></html>")

		elif self.path == '/pynp':
			self._set_headers()		
			content_len = int(self.headers.getheader('content-length'))
			post_body = self.rfile.read(content_len)
			vars = self._parse_post(post_body)
			self.wfile.write("<html><body>")
			if vars:
				try:
					messages = []
					user = cryp.decode(vars['key'])
					if vars.get("output"): messages.append("%s" % urllib2.unquote(vars['status']).replace('+', ' '))
					if len(messages) > 0:
						#Send messages to bots
						for loc in SenderIns.senders:
							if loc.assets['config']['osu_np'].get(user):
								for chan in loc.assets['config']['osu_np'][user]:
									loc.message( "13[Osu!] [10%s13]14 %s" % (user, " - ".join(messages)), chan, False )
								self.wfile.write("<h1>[%s] Accepted</h1>" % loc.nick)
							else:
								self.wfile.write("<h1>[%s] Access denied!</h1>" % loc.nick)
					else: self.wfile.write("<h1>No message to send!</h1>")
				except Exception, e: self.wfile.write("<h1>Exception ocurred %s</h1>" % str(e))
				self.wfile.write("</body></html>")
		
		else:
			self._set_headers(404)
        
class SenderIns:
	senders = []
		
class OsunpServer:
	def __init__(self, port, sender):
		SenderIns.senders = sender
		self.port = port
		self.server = HTTPServer(('', port), osunp_handler_class)
		
	def start(self):
		print "[+] Osu!np server started on port %s" % self.port 
		self.server.serve_forever()
		
	def stop(self):
		self.server.shutdown()
		print "[-] Osu!np server stopped"
	
