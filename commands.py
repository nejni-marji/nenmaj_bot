#!/usr/bin/env python3
import sqlite3
from os.path import dirname
from time import sleep
from urllib.request import urlopen
from json import loads
from re import match
from datetime import datetime
from pytz import timezone

import telegram as tg
import telegram.ext as tg_ext

from bin.background import background

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

def timezones(bot, update):
	resp = []
	time_file = open(dirname(__file__) + '/private/time.json')
	time_dict = loads(time_file.read())
	time_file.close()
	if str(update.message.chat_id) in time_dict:
		for i in time_dict[str(update.message.chat_id)]:
			time = datetime.now(tz = timezone(i[0]))
			zone = '<code>{}:</code> {}'.format(
				time.strftime('%H:%M (%Z)'),
				i[1]
			)
			resp.append(zone)
		bot.send_message(
			update.message.chat_id,
			'\n'.join(resp),
			parse_mode = tg.ParseMode.HTML
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

def main(dp):
	dp.add_handler(tg_ext.CommandHandler('start', start))
	dp.add_handler(tg_ext.CommandHandler('nenmaj', nenmaj))
	dp.add_handler(tg_ext.CommandHandler('nm', nenmaj))
	dp.add_handler(tg_ext.CommandHandler('donate', donate))
	dp.add_handler(tg_ext.CommandHandler('sudo', sudo, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('btc', btc))
	dp.add_handler(tg_ext.CommandHandler('time', timezones))
	dp.add_handler(tg_ext.CommandHandler('calc', calc, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('motd', motd, pass_args = True))

	dp.add_handler(tg_ext.CommandHandler('echo', echo, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('echom', echom, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('echon', echon, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('echomn', echomn, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('e', echo, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('em', echom, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('en', echon, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('emn', echomn, pass_args = True))

	dp.add_handler(tg_ext.CommandHandler('hic', hi_c))
	dp.add_handler(tg_ext.CommandHandler('foss', foss))
