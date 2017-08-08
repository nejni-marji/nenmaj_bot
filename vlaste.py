#!/usr/bin/env python3
from os.path import dirname
from xml.etree.ElementTree import parse
import re

import telegram as tg
import telegram.ext as tg_ext

from bin.background import background

myself = int(open(dirname(__file__) + '/private/myself').read())

class Dictionary():
	def __init__(self):
		self.root = parse(dirname(__file__) + '/private/lojban_english.xml').getroot()
		self.jbo = self.root[0].getchildren()
		self.en = self.root[1].getchildren()

dictionary = Dictionary()

def clean(definition):
	if not definition: return 'Undefined'
	for i in re.findall('\$[^$]+\$', definition):
		definition = definition.replace(i, re.sub('\$?(?<=[$=])([a-z]+)_\{?(\\d)+\}?(?=[$=])\$?', '\\1\\2', i), 1)
	return definition

def get_gloss(valsi):
	return '\n'.join(
		[clean(valsi.find('definition').text)]
		+ [' ; '.join([gloss.attrib[i] for i in gloss.attrib]) for gloss in valsi.findall('glossword')]
	)

def score_word(valsi, query):
	if query in [gloss.attrib['word'] for gloss in valsi.findall('glossword')]:
		return 0
	if True in [query in gloss.attrib['word'] for gloss in valsi.findall('glossword')]:
		return 1
	return 2

@background
def jboen(bot, update, args):
	query = args[0].lower()
	try: #TODO: fix
		valsi = [valsi for valsi in dictionary.jbo if query == valsi.attrib['word'].lower()][0]
	except:
		return None
	definition = clean(valsi.find('definition').text)
	resp = '{}: {}'.format(valsi.attrib['word'], definition)
	bot.send_message(update.message.chat_id, resp)

@background
def enjbo(bot, update, args):
	query = args[0].lower()
	results = [valsi for valsi in dictionary.jbo if query in get_gloss(valsi).lower()]
	matches = [ [], [], [] ]
	for valsi in results:
		matches[score_word(valsi, query)].append(valsi.attrib['word'])
	resp = '\n'.join([', '.join(i) for i in matches])
	bot.send_message(update.message.chat_id, resp)

def main(dp):
	dp.add_handler(tg_ext.CommandHandler('jboen', jboen, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('enjbo', enjbo, pass_args = True))
