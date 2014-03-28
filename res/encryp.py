#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-
import re, math, random

class Encryp:
	def __init__(self, hash = "abcdefghijklmnopqrstvwxyz1234567890"):
		self.hash = hash
		
	def newhash(self):
		return "".join(random.sample(self.hash,len(self.hash)))
		
	def gethast(self):
		return self.hash
		
	def encode(self, text):
		n = float(len( text ) * 8) / 5
		m = ""
		for c in text: m += "{0:b}".format(ord(c)).rjust(8,"0")
		p = int(math.ceil(float(len(m))/5)*5)
		m = m.ljust(p,"0")
		newstr = ""
		i = 0
		while i < n:
			newstr += self.hash[int(m[(i*5):5+(i*5)],2)]
			i += 1
		return newstr
		
	def decode(self, text):
		n = float(len(text)*5) / 8
		m = ""
		try: 
			for c in text: m += "{0:b}".format(self.hash.index(c)).rjust(5,"0")
		except: return False
		oldstr = ""
		i = 0
		while i < math.floor(n):
			oldstr += chr(int(m[(i*8):8+(i*8)],2))
			i += 1
		return oldstr