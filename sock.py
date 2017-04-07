#!/usr/bin/env python3
from os.path import dirname

import telegram as tg
import telegram.ext as tg_ext

myself = int(open(dirname(__file__) + '/private/myself').read())

SOCK = range(1)
source, target = 0, 0

def cancel(bot, update):
	global source, target
	source, target = 0, 0
	bot.send_message(update.message.chat_id,
		'Done.'
	)
	return tg_ext.ConversationHandler.END

def sock(bot, update, args, user_data):
	if not update.message.from_user.id == myself:
		return None
	user_data['source'] = update.message.chat_id
	try:
		user_data['target'] = int(args[0])
	except:
		user_data['target'] = int(update.message.from_user.id)
	global source, target
	source = user_data['source']
	target = user_data['target']
	bot.send_message(update.message.chat.id,
		'Beginning sock with %i.' % user_data['target']
	)
	return SOCK

def send(bot, update, args, user_data):
	bot.send_message(user_data['target'],
		' '.join(args),
		parse_mode = tg.ParseMode.HTML,
	)
	return SOCK

def send_text(bot, update, user_data):
	bot.send_message(user_data['target'],
		update.message.text,
		parse_mode = tg.ParseMode.HTML,
	)

conv_handler = tg_ext.ConversationHandler(
	entry_points = [
		tg_ext.CommandHandler('sock', sock, pass_args = True, pass_user_data = True),
	],

	states = {
		SOCK: [
			tg_ext.CommandHandler('sock', sock, pass_args = True, pass_user_data = True),
			tg_ext.CommandHandler('send', send, pass_args = True, pass_user_data = True),
			tg_ext.CommandHandler('s', send, pass_args = True, pass_user_data = True),
			tg_ext.MessageHandler(tg_ext.Filters.text, send_text, pass_user_data = True)
		],
	},

	fallbacks = [
		tg_ext.CommandHandler('cancel', cancel),
		tg_ext.CommandHandler('done', cancel),
		tg_ext.CommandHandler('exit', cancel),
		tg_ext.CommandHandler('quit', cancel),
		tg_ext.CommandHandler('q', cancel),
	],
)

def forward(bot, update):
	if update.message.chat_id == target:
		bot.forward_message(
			chat_id = source,
			from_chat_id = target,
			message_id = update.message.message_id,
		)


def main(dp):
	dp.add_handler(conv_handler, group = 2)
	dp.add_handler(tg_ext.MessageHandler(tg_ext.Filters.all, forward), group = 2)
