#!/usr/bin/env python3
from os.path import dirname
from json import loads
from argparse import ArgumentParser
from random import randint

import telegram as tg
import telegram.ext as tg_ext

from bin.config import *
from commands import sudo

myself = int(open(dirname(__file__) + '/private/myself').read())

parsers = {}
for i in ['set', 'get', 'del']:
	parser = parsers[i] = ArgumentParser(
			prog = '/{} | /{}'.format(i, i[0]),
			prefix_chars = '.',
			add_help = False
			)
	parser.add_argument(
		'key',
		nargs = '?', #TODO make sure this works
	)
	parsers[i].add_argument(
		'.h', '..help',
		action = 'store_true', dest = 'help',
	)
	parser.add_argument(
		'.c', '..chat',
		action = 'store_true', dest = 'chat',
	)
	parser.add_argument(
		'.u', '..user',
		action = 'store_true', dest = 'user',
	)
	parser.add_argument(
		'.a', '..absolute',
		action = 'store_true', dest = 'absolute',
	)

parsers['set'].add_argument(
	'value',
	nargs = '*',
)

parsers['get'].add_argument(
	'.g', '..give',
	action = 'store_true',
	dest = 'give',
)

reg_parser = ArgumentParser(
	prog = '/reg | /r',
	prefix_chars = '.',
	add_help = False
)
reg_parser.add_argument(
	'.c', '..chat',
	action = 'store_true', dest = 'chat',
)
reg_parser.add_argument(
	'.u', '..user',
	action = 'store_true', dest = 'user',
)
reg_parser.add_argument(
	'query',
	nargs = '*',
)

class Option():
	def __init__(self, bot, update, args, mode):
		if not mode in parsers:
			return None

		self.get_vars(bot, update, args, mode)
		self.get_keys(self.args)
		try:
			self.key
			self.dotkey
		except:
			return None
		self.get_value()
		self.get_conf()
		self.get_resp()
		self.send_resp()

	def send_help(self):
		self.bot.send_message(
			self.chat_id,
			'```\n' + parsers[self.mode].format_help() + '\n```',
			**self.kwargs
		)

	def get_vars(self, bot, update, args, mode):
		self.bot, self.update = bot, update
		self.chat_id = str(update.message.chat_id)
		self.user_id = str(update.message.from_user.id)
		self.mesg_id = str(update.message.message_id)

		self.args = parsers[mode].parse_args(args)
		self.mode = mode

		self.kwargs = {
			'parse_mode': tg.ParseMode.MARKDOWN,
			'reply_to_message_id': self.mesg_id
		}

	def get_keys(self, args):
		if not self.user_id == str(myself):
			args.absolute = False

		if args.absolute:
			args.chat = False
			args.user = False

		no_key = not (args.key or args.chat or args.user)
		if args.help or no_key:
			self.send_help()
			return None

		if not args.key:
			args.key = str()
		dotkey = args.key
		key = args.key.split('.')

		if key == [str()]:
			key = []

		if not args.absolute:
			if args.chat and args.user:
				dotkey = 'user.chat.' + dotkey
				key = [self.chat_id] + key
				key = ['chats'] + key
				key = [self.user_id] + key
			elif args.chat:
				dotkey = 'chat.' + dotkey
				key = [self.chat_id] + key
			elif args.user:
				dotkey = 'user.' + dotkey
				key = [self.user_id] + key

			if not args.chat and not args.user:
				key = [self.chat_id] + key
				if int(self.chat_id) > 0:
					dotkey = 'user.' + dotkey
				else:
					dotkey = 'chat.' + dotkey

			if dotkey.startswith('chat.') and not sudo(self.bot, self.update, 'quiet'):
				sudo(self.bot, self.update, 'test')
				return None

			if dotkey.endswith('.'):
				dotkey = dotkey[:-1]

		self.key, self.dotkey = key, dotkey

	def get_value(self):
		if self.mode == 'set':
			self.value = ' '.join(self.args.value)
			return None

		value = get_conf(self.key)

		def clean_value(value):
			if type(value) == str:
				return value
			elif type(value) == dict:
				return {}
			return type(value).__name__

		if type(value) == dict:
			value = {
				i: clean_value(value[i])
				for i in value
			}

		self.value = value

	def get_conf(self):
		self.conf = {
			'set': self.set_key,
			'get': self.get_key,
			'del': self.del_key,
		}[self.mode]()

	def get_resp(self):
		if self.mode == 'set' and self.conf:
			self.resp = self.conf
		if self.mode == 'get' and self.args.give:
			self.resp = self.value
			del self.kwargs['parse_mode']
		else:
			self.resp = '{} {}: {}'.format(
				self.mode,
				self.dotkey,
				self.value
			)
			self.resp = '```\n{}\n```'.format(self.resp)

	def send_resp(self):
		self.bot.send_message(
			self.chat_id,
			self.resp,
			**self.kwargs
		)

	def set_key(self):
		return set_conf(self.key, self.value)

	def get_key(self):
		return get_conf(self.key)

	def del_key(self):
		return del_conf(self.key)

def set_parser(bot, update, args):
	Option(bot, update, args, 'set')

def get_parser(bot, update, args):
	Option(bot, update, args, 'get')

def del_parser(bot, update, args):
	Option(bot, update, args, 'del')

def register(bot, update):
	if not randint(1, 1) == 1:
		return None
	# register chat data
	chat = update.message.chat
	set_conf(
		'reg.{}.title'.format(chat.id),
		chat.title
	)

	# register user data
	user = update.message.from_user
	path = 'reg.{}.'.format(user.id)
	set_conf(
		path + 'first_name',
		user.first_name
	)
	set_conf(
		path + 'last_name',
		user.last_name
	)
	set_conf(
		path + 'username',
		user.username
	)
	name = user.first_name
	if user.last_name: name += ' ' + user.last_name
	set_conf(
		path + 'name',
		name
	)

	# register reg.*.names
	set_conf(
		'reg.{}.names'.format(user.id),
		'{} {}'.format(
			user.username, name
		).lower()
	)
	# only register title if chat
	if chat.id < 0:
		set_conf(
			'reg.{}.names'.format(chat.id),
			chat.title.lower()
		)

def registry_search(bot, update, args):
	if not update.message.from_user.id == myself:
		return None
	args = reg_parser.parse_args(args)
	query = ' '.join(args.query).lower()
	reg = get_conf('reg')

	def respect_args(num):
		if args.chat == args.user:
			return True
		if args.chat and int(num) < 0:
			return True
		if args.user and int(num) > 0:
			return True
		return False

	def clean_names(num):
		if int(num) > 0:
			user = reg[num]
			resp = num + ': ' + user['name']
			if user['username']:
				resp += ' (@{})'.format(user['username'])
		else:
			chat = reg[num]
			resp = num + ': ' + chat['title']
		return resp

	resp = '\n'.join([
		clean_names(i)
		for i in reg
		if respect_args(i)
		and query in reg[i]['names']
	])
	if resp:
		bot.send_message(
			update.message.chat_id,
			resp,
		)

def main(dp, group):
	for i in [
		tg_ext.CommandHandler('set', set_parser, pass_args = True),
		tg_ext.CommandHandler('get', get_parser, pass_args = True),
		tg_ext.CommandHandler('del', del_parser, pass_args = True),
		tg_ext.CommandHandler('reg', registry_search, pass_args = True),
		tg_ext.CommandHandler('s', set_parser, pass_args = True),
		tg_ext.CommandHandler('g', get_parser, pass_args = True),
		tg_ext.CommandHandler('d', del_parser, pass_args = True),
		tg_ext.CommandHandler('r', registry_search, pass_args = True),
		tg_ext.MessageHandler(tg_ext.Filters.all, register),
	]: dp.add_handler(i, group)
