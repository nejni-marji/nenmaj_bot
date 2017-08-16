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

def pre_parser(bot, update, args, mode):
	if not update.message.from_user.id == myself:
		args.absolute = False
	if args.absolute:
		args.chat = False
		args.user = False

	no_key = not (args.key or args.chat or args.user)
	if args.help or no_key:
		bot.send_message(
			update.message.chat_id,
			'```\n' + parsers[mode].format_help() + '\n```',
			parse_mode = tg.ParseMode.MARKDOWN
		)
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
			key = [str(update.message.chat_id)] + key
			key = ['chats'] + key
			key = [str(update.message.from_user.id)] + key
		elif args.chat:
			dotkey = 'chat.' + dotkey
			key = [str(update.message.chat_id)] + key
		elif args.user:
			dotkey = 'user.' + dotkey
			key = [str(update.message.from_user.id)] + key

		if not args.chat and not args.user:
			key = [str(update.message.chat_id)] + key
			if update.message.chat_id > 0:
				dotkey = 'user.' + dotkey
			else:
				dotkey = 'chat.' + dotkey

		if dotkey.startswith('chat.') and not sudo(bot, update, 'quiet'):
			sudo(bot, update, 'test')
			return None

		if dotkey.endswith('.'):
			dotkey = dotkey[:-1]

	if 'value' in args and args.value:
		value = ' '.join(args.value)
	else:
		value = get_conf(key)
	if 'give' in args and args.give:
		text = value
	else:
		def clean_value(value):
			t = type(value)
			if t == str:
				return value
			elif t == dict:
				return {}
			return type(value).__name__
		if type(value) == dict:
			value = {
				i: clean_value(value[i])
				for i in value
			}
		text = '```\n{} {}: {}\n```'.format(
			mode, dotkey, value
		)
		bot_kwargs = {
			'chat_id': update.message.chat_id,
			'text': text,
			'parse_mode': tg.ParseMode.MARKDOWN,
			'reply_to_message_id': update.message.message_id
		}

	return {
		'dotkey': dotkey,
		'key': key,
		'value': value,
		'kwargs': bot_kwargs,
	}

def set_parser(bot, update, args):
	try:
		if type(args) == str:
			args = args.split()
		args = parsers['set'].parse_args(args)
		if not args.value:
			args.help = True
	except:
		return None
	new_args = pre_parser(bot, update, args, 'set')
	if not new_args:
		return None
	set_conf(new_args['key'], new_args['value'])
	bot.send_message(**new_args['kwargs'])

def get_parser(bot, update, args):
	try:
		if type(args) == str:
			args = args.split()
		args = parsers['get'].parse_args(args)
	except:
		return None
	new_args = pre_parser(bot, update, args, 'get')
	if not new_args:
		return None
	get_conf(new_args['key'])
	bot.send_message(**new_args['kwargs'])

def del_parser(bot, update, args):
	try:
		if type(args) == str:
			args = args.split()
		args = parsers['get'].parse_args(args)
	except:
		return None
	new_args = pre_parser(bot, update, args, 'del')
	if not new_args:
		return None
	del_conf(new_args['key'])
	bot.send_message(**new_args['kwargs'])

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
