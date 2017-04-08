#!/usr/bin/env python3
from os.path import dirname
from random import randint
from time import sleep
from urllib.request import urlopen
from json import loads

import telegram as tg
import telegram.ext as tg_ext

import bin.database as db
from bin.background import background

class Comic():
	def __init__(self):
		self.lock = True
		self.get_db()
	def get_json_unsafe(self, num = ''):
		if not isinstance(num, int):
			num = ''
		if num == 404:
			return {
				'month': '9',
				'num': '404',
				'link': '',
				'year': '404',
				'news': '',
				'safe_title': '404',
				'transcript': '404',
				'alt': '404',
				'img': 'https://xkcd.com/s/0b7742.png',
				'title': '404',
				'day': '404',
			}
		site= "https://xkcd.com/{}/info.0.json"
		print('Getting ' + site.format(num)) #debug
		# this is how many times the dl can fail before we quit
		count = 3
		while count:
			count -= 1
			try:
				data = urlopen(site.format(num))
				count = 0
			except:
				print('Failed to download JSON ' + str(num))
		data = data.read()
		data = data.decode()
		data = loads(data)
		return data
	def wait_lock(self): # unused?
		locked = self.lock
		if locked:
			print('Waiting for lock.')
		while self.lock:
			sleep(1)
		if locked:
			print('Database unlocked.')
		return None
	def pprint(self, data):
		for i in data:
			print('{}:\n{}\n'.format(i, data[i]))
		return None
	def pprint2(self, data_list):
		for i in data_list:
			print('{}: {}'.format(i['num'], i['title']))
	def init_db(self):
		comic_db = [self.get_json_unsafe()] #debug
		latest = comic_db[0]['num']
		for i in range(1, latest):
			comic_db.append(self.get_json_unsafe(i))
		comic_db.append(comic_db[0])
		print('Done initializing database')
		return comic_db
	@background
	def get_db(self):
		self.comic_db = db.start('private/comic.json', self.init_db)
		# check if an update is necessary
		self.comic_db[0] = self.get_json_unsafe()
		true_latest = self.comic_db[0]['num']
		dled_latest = len(self.comic_db) - 1
		print('true_latest: ' + str(true_latest))
		print('dled_latest: ' + str(dled_latest))
		if not true_latest == dled_latest:
			print('Updating database')
			for i in range(dled_latest + 1, true_latest):
				self.comic_db.append(self.get_json_unsafe(i))
			self.comic_db.append(self.comic_db[0])
		db.dump('private/comic.json', self.comic_db)
		print('Done updating database')
		self.lock = False
	def num_query(self, num = 'latest'):
		if num in ['latest', 'l']:
			num = 0
		if num in ['random', 'rand', 'r']:
			rand_list = range(len(self.comic_db))
			num = rand_list[randint(1, len(rand_list) - 1)]
		try:
			result = self.comic_db[int(num)]
			count = 0
			return result
		except:
			return self.num_query(404)

comic = Comic()

def xkcd_num(bot, update, args):
	try:
		result = comic.num_query(args[0])
	except:
		result = comic.num_query('latest')
	bot.send_photo(update.message.chat_id,
		result['img'],
		caption = '{}: {}: {}'.format(*(result[i] for i in ['num', 'title', 'alt'])),
		reply_to_message_id = update.message.message_id,
	)
def xkcd_search(bot, update, args):
	if not args:
		return None
	query = ' '.join(args)
	result = []
	for i in comic.comic_db[1:]:
		if True in (query.lower() in i[j].lower() for j in ['title', 'transcript', 'alt']):
			result.append('{}: {}'.format(i['num'], i['title']))
	if result:
		resp = '\n'.join(result)
	else:
		resp = 'No results.'
	try:
		bot.send_message(update.message.chat_id,
			resp,
			reply_to_message_id = update.message.message_id,
		)
	except:
		bot.send_message(update.message.chat_id,
			'Too many results to display.',
			reply_to_message_id = update.message.message_id,
		)

def main(dp):
	dp.add_handler(tg_ext.CommandHandler('xkcd', xkcd_num, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('x', xkcd_num, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('search', xkcd_search, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('s', xkcd_search, pass_args = True))
