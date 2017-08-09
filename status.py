#!/usr/bin/env python3
from os.path import dirname

import telegram as tg
import telegram.ext as tg_ext

myself = int(open(dirname(__file__) + '/private/myself').read())

def status(bot, update):
	try:
		if update.message.left_chat_member.id == bot.id:
			bot.send_message(myself,
				'{} ({}) has removed me from a chat:\n{}:\n{}'.format(
					update.message.from_user.first_name,
					update.message.from_user.id,
					update.message.chat.title,
					update.message.chat_id
				)
			)
	except AttributeError:
		pass

def main(dp, group):
	for i in [
		tg_ext.MessageHandler(tg_ext.Filters.status_update, status),
	]: dp.add_handler(i, group)
