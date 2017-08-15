#!/usr/bin/env python3
import sqlite3
from os.path import dirname
from time import sleep
from urllib.request import urlopen
from json import loads
from re import match
from geopy import geocoders
from datetime import datetime
from pytz import timezone

import telegram as tg
import telegram.ext as tg_ext

from bin.background import background
from bin.config import set_conf, get_conf, check_conf

myself = int(open(dirname(__file__) + '/private/myself').read())

# general commands

def start(bot, update):
	bot.send_message(update.message.chat.id, 'Komencita!')

def nenmaj(bot, update):
	bot.send_message(update.message.chat_id,
		'Mi ĉeestas~!'
	)

def donate(bot, update):
	bot.send_message(update.message.chat_id,
		# This Bitcoin address belongs to me, nejni marji. If you want to fork
		# my bot, I'd rather you not change this unless you make significant
		# changes to the code. Thanks!
		"Sendu bitmonon al / Send bitcoin to:\n"
		+ "1Jn3cbFkFcPGwZLTtFxttUgNFAsZDBy4VV",
		reply_to_message_id = update.message.message_id,
	)

def sudo(bot, update, args):
	private = update.message.chat_id > 0
	master = update.message.from_user.id == myself
	status = bot.get_chat_member(
		update.message.chat_id,
		update.message.from_user.id,
	).status
	creator = status == 'creator'
	admin = status == 'administrator'
	if True in (master, private, creator, admin):
		permit = True
	else:
		permit = False
	if not 'quiet' in args:
		resp = 'Sudo Access: {}'.format(str(permit))
		bot.send_message(update.message.chat_id,
			resp,
			reply_to_message_id = update.message.message_id,
		)
	return permit

@background
def btc(bot, update):
	url = 'https://api.gemini.com/v1/pubticker/btcusd'
	text = urlopen(url).read()
	data = loads(text.decode('utf8'))

	ask = float(data['ask'])
	bid = float(data['bid'])
	last = float(data['last'])
	spread = ask-bid

	resp = []
	resp.append('BTC-USD (Gemini):')
	resp.append('Ask: %.2f' % ask)
	resp.append('Bid: %.2f' % bid)
	resp.append('Last: %.2f' % last)
	resp.append('Spread: %.2f' % spread)

	msg = bot.send_message(update.message.chat_id,
		'\n'.join(resp),
		reply_to_message_id = update.message.message_id,
	)

geocoder = geocoders.GoogleV3()
def set_timezone(bot, update, args):
	query = ' '.join(args)
	place, pos = geocoder.geocode(query)
	zone = geocoder.timezone(pos).zone

	key = 'reg.%i.' % update.message.from_user.id
	set_conf(key + 'location', query)
	set_conf(key + 'timezone', zone)
	user_chat = '%i.chats.%i' % (
		update.message.from_user.id,
		update.message.chat_id
	)
	set_conf(
		user_chat + '.timezone.enabled',
		'on'
	)

	bot.send_message(
		update.message.chat_id,
		'Set timezone: {}'.format(place)
	)

def get_timezone(bot, update):
	if update.message.chat_id > 0:
		return None

	reg = get_conf('reg')

	def check_user(user_id):
		if not 'timezone' in reg[user_id]:
			return False

		status = bot.get_chat_member(
			update.message.chat_id, user_id
		).status
		if not status in ['creator', 'administrator', 'member']:
			return False

		if not check_conf(
			'{}.chats.{}.timezone.enabled'.format(
				user_id, update.message.chat_id
			), bool, False
		):
			return False

		return True

	users = [reg[i] for i in reg if check_user(i)]
	zones = [i['timezone'] for i in users]

	zones = {
		int(datetime.now(tz = timezone(i)).strftime('%z')): i
		for i in zones
	}
	offsets = list(zones)
	offsets.sort()
	resp = '\n'.join([
		'{}: {}'.format(
			datetime.now(tz = timezone(zones[i])).strftime('%H:%M (%Z)'),
			', '.join([
				j['first_name'] for j in users
				if zones[i] == j['timezone']
			])
		)
		for i in offsets
	])
	bot.send_message(
		update.message.chat_id, resp
	)


def calc(bot, update, args):
	if not sudo(bot, update, 'quiet'):
		sudo(bot, update, 'test')
		return None
	if match('^[0-9.()*/+-]+$', ' '.join(args)):
		resp = eval(' '.join(args))
		bot.send_message(update.message.chat_id,
			resp,
		)

def motd(bot, update, args):
	#TODO make this function prettier
	if args:
		# check perms before letting someone set the MOTD
		if not sudo(bot, update, 'quiet'):
			sudo(bot, update, 'test')
			return None
		conn = sqlite3.connect(dirname(__file__) + '/private/chats.db')
		data = {'chat_id': update.message.chat_id, 'message': ' '.join(args)}
		# SQL UPSERT
		conn.execute(
			'UPDATE motd\n'
			+ 'SET message = :message\n'
			+ 'WHERE chat_id = :chat_id;',
			data
		)
		conn.execute(
			'INSERT INTO motd (chat_id, message)\n'
			+ 'SELECT :chat_id, :message\n'
			+ 'WHERE (Select Changes() = 0);',
			data
		)
		conn.commit()
		resp = 'Set MOTD.'
	else:
		conn = sqlite3.connect(dirname(__file__) + '/private/chats.db')
		data = {'chat_id': update.message.chat_id}
		# SQL SELECT
		resp = 'MOTD:\n' + conn.execute(
			'SELECT message FROM motd\n'
			+ 'WHERE chat_id = :chat_id',
			data
		).fetchone()[0]
	conn.close()
	if resp == None: resp = 'MOTD is not set.'
	bot.send_message(update.message.chat_id,
		resp,
		reply_to_message_id = update.message.message_id,
	)

def echo(bot, update, args, i = 1, n = 1, markdown = False):
	bot_kwargs = {}
	if markdown:
		bot_kwargs = {'parse_mode': tg.ParseMode.HTML}
	try:
		reply = update.message.reply_to_message.message_id
	except:
		reply = False
	forward = not args

	if forward and reply:
		# forward message
		bot.forward_message(
			chat_id = update.message.chat_id,
			from_chat_id = update.message.chat_id,
			message_id = update.message.reply_to_message.message_id,
			**bot_kwargs
		)
	elif not forward and reply:
		# echo with reply
		bot.send_message(update.message.chat_id,
			' '.join(args).format(
				chat_title = update.message.chat.title,
				chat_id = update.message.chat_id,
				nl = '\n', i = i, n = n,
			),
			reply_to_message_id = reply,
			**bot_kwargs
		)
	elif not forward and not reply:
		# echo
		bot.send_message(update.message.chat_id,
			' '.join(args).format(
				chat_title = update.message.chat.title,
				chat_id = update.message.chat_id,
				nl = '\n', i = i, n = n,
			),
			**bot_kwargs
		)
	elif forward and not reply:
		bot.send_message(update.message.chat_id,
			'Vi povas igi, ke mi diru ion per ĉi tiu komando. '
			+ 'Aldone, vi povas uzi {nl} anstataŭ vera novlineo.'
		)

def echom(bot, update, args):
	echo(bot, update, args, i = 1, n = 1, markdown = True)

@background
def echon(bot, update, args, markdown = True):
	if markdown:
		bot_kwargs = {'markdown': True}
	bot.forward_message(
		myself,
		from_chat_id = update.message.chat_id,
		message_id = update.message.message_id,
	)
	if not sudo(bot, update, 'quiet'):
		sudo(bot, update, 'test')
		return None
	try:
		if args[0]:
			n = int(args[0])
		if n:
			args.pop(0)
			for i in range(1, n + 1):
				sleep(1)
				echo(bot, update, args, i = i, n = n, **bot_kwargs)
	except:
		bot.send_message(update.message.chat_id,
			'La unua afero en la mesaĝo devas esti numero:\n'
			+ '`/echon 5 [mesaĝo]`',
			parse_mode = tg.ParseMode.MARKDOWN,
		)

@background
def echomn(bot, update, args):
	echon(bot, update, args)

# dumb commands

def hi_c(bot, update):
	bot.send_photo(update.message.chat_id,
		"AgADBAADEfQ2G_UdZAd8j4h2V8eoRzRUoBkABBr6NkYuexXAhBECAAEC"
	)

def foss(bot, update):
	bot.send_photo(update.message.chat_id,
		"AgADAwADrKcxGxf4GExRki2M2qyrKI30hjEABLCGgdjm9eXSgEYBAAEC"
	)

def main(dp, group):
	for i in [
		tg_ext.CommandHandler('start', start),
		tg_ext.CommandHandler('nenmaj', nenmaj),
		tg_ext.CommandHandler('nm', nenmaj),
		tg_ext.CommandHandler('donate', donate),
		tg_ext.CommandHandler('sudo', sudo, pass_args = True),
		tg_ext.CommandHandler('btc', btc),
		tg_ext.CommandHandler('timezone', set_timezone, pass_args = True),
		tg_ext.CommandHandler('time', get_timezone),
		tg_ext.CommandHandler('calc', calc, pass_args = True),
		tg_ext.CommandHandler('motd', motd, pass_args = True),

		tg_ext.CommandHandler('echo', echo, pass_args = True),
		tg_ext.CommandHandler('echom', echom, pass_args = True),
		tg_ext.CommandHandler('echon', echon, pass_args = True),
		tg_ext.CommandHandler('echomn', echomn, pass_args = True),
		tg_ext.CommandHandler('e', echo, pass_args = True),
		tg_ext.CommandHandler('em', echom, pass_args = True),
		tg_ext.CommandHandler('en', echon, pass_args = True),
		tg_ext.CommandHandler('emn', echomn, pass_args = True),

		tg_ext.CommandHandler('hic', hi_c),
		tg_ext.CommandHandler('foss', foss),
	]: dp.add_handler(i, group)
