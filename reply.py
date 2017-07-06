#!/usr/bin/env python3
from os.path import dirname
from random import randint

import telegram as tg
import telegram.ext as tg_ext

myself = int(open(dirname(__file__) + '/private/myself').read())

def reply_check(bot, update):
	msg = update.message
	# don't notify about me or my bot
	if msg.from_user.id in (myself, bot.id):
		return None
	# check if there is a reply to me or my bot
	try:
		reply = (msg.reply_to_message.from_user.id in (myself, bot.id))
	except AttributeError:
		reply = False
	# list of my names
	alert_list = ['nejni', 'marji', 'nenmaj', 'neĵni', 'neĵ']
	# check if I am named
	try:
		alert = (True in (i in msg.text.lower() for i in alert_list))
	except AttributeError:
		alert = False
	# kill undesireables
	if not reply and not alert: return None

	# get message info
	chat = update.message.chat.id
	try:
		user = update.from_user
	except AttributeError:
		user = update.message.from_user
	member = bot.get_chat_member(
		chat, user.id
	)

	# put message info into list
	resp = []
	# chat
	resp.append(str(msg.date))
	if msg.chat.title: resp.append(str(msg.chat.title) + ':')
	else: resp.append(':')
	resp.append(str(msg.chat.id))
	# user
	resp.append(str(user.id))
	if user.username:
		resp[3] += ' (@%s)' % user.username
	resp.append('P-nomo: ' + user.first_name)
	if user.last_name:
		resp.append('F-nomo: ' + user.last_name)
	resp.append('Stato: %s' % member.status)

	# send alert
	bot.send_message(
		chat_id = myself,
		text = '\n'.join(resp)
	)

	if reply:
		bot.forward_message(
			chat_id = myself,
			from_chat_id = msg.chat.id,
			message_id = msg.reply_to_message.message_id
		)

	bot.forward_message(
		chat_id = myself,
		from_chat_id = msg.chat.id,
		message_id = msg.message_id
	)

def main(dp):
	dp.add_handler(tg_ext.MessageHandler(tg_ext.Filters.all, reply_check), group = 1)
