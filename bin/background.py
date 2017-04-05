#!/usr/bin/env python3
from threading import Thread

def background(func):
	def threader(*args, **kwargs):
		p = Thread(
			target = func,
			args = args,
			kwargs = kwargs,
		)
		p.start()
	return threader
