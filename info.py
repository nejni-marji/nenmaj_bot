#!/usr/bin/env python3
import telegram as tg
import telegram.ext as tg_ext

#TODO:
# Redo variables,
# Don't ever create variables to shorten the code.
# Always refer directly to `update'.

def info_meta(bot, update, args):
	commands = {
		'user':    info_user,
		'u':       info_user,
		'chat':    info_chat,
		'c':       info_chat,
		'message': info_message,
		'm':       info_message,
		'forward': info_forward,
		'f':       info_forward,
		'full' :   info_full,
		'F':       info_full,
	}
	try:
		commands[args[0]](bot, update, args)
	except:
		resp = 'Uzado: `/info [{}]`'.format('|'.join(i for i in commands))
		bot.send_message(update.message.chat_id,
			resp,
			parse_mode = tg.ParseMode.MARKDOWN,
		)
def info_user(bot, update, args):
	chat_id = update.message.chat_id
	if update.message.reply_to_message:
		user_id = update.message.reply_to_message.from_user.id
	else:
		try:
			user_id = args[1]
		except:
			user_id = args[0]
	member = bot.get_chat_member(
		chat_id, user_id
	)
	user = member.user
	# make info
	resp = ''
	resp += str(user.id)
	if user.username:
		resp += ' (@%s)' % user.username
	resp += '\nP-nomo: ' + user.first_name
	if user.last_name:
		resp += '\nF-nomo: ' + user.last_name
	if chat_id < 0:
		resp += '\nStato: %s' % member.status
	# send info
	bot.send_message(
		update.message.chat.id, resp,
		reply_to_message_id = update.message.message_id
	)
def info_chat(bot, update, args):
	chat = update.message.chat
	if chat.id < 0:
		resp = '{}:\n{}'.format(chat.title, chat.id)
	else:
		user_id = update.message.from_user.id
		member = bot.get_chat_member(
			chat.id, user_id
		)
		user = member.user
		resp = ''
		resp += str(user.id)
		if user.username:
			resp += ' (@%s)' % user.username
		resp += '\nP-nomo: ' + user.first_name
		if user.last_name:
			resp += '\nF-nomo: ' + user.last_name
		if chat.id > 0:
			resp += '\nStato: %s' % member.status
	bot.send_message(
		update.message.chat.id, resp,
		reply_to_message_id = update.message.message_id
	)
def info_message(bot, update, args): # fixed
	resp = update.message.reply_to_message.message_id
	bot.send_message(
		update.message.chat_id, resp,
		reply_to_message_id = update.message.message_id
	)
def info_forward(bot, update, args):
	user = update.message.reply_to_message.forward_from
	chat_id = update.message.chat_id
	# make info
	resp = ''
	resp += str(user.id)
	if user.username:
		resp += ' (@%s)' % user.username
	resp += '\nP-nomo: ' + user.first_name
	if user.last_name:
		resp += '\nF-nomo: ' + user.last_name
	if chat_id < 0:
		resp += '\nStato: %s' % member.status
	# send info
	bot.send_message(
		update.message.chat.id, resp,
		reply_to_message_id = update.message.message_id
	)
def info_full(bot, update, args):
	message = update.message.reply_to_message
	resp = 'Mi rekte mesaĝu al vi la detalojn de la mesaĝo.'
	bot.send_message(
		update.message.chat_id, resp,
		reply_to_message_id = update.message.message_id
	)
	bot.send_message(update.message.from_user.id,
		str(update.message.reply_to_message)
	)
def main(dp):
	dp.add_handler(tg_ext.CommandHandler('info', info_meta, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('i', info_meta, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('iu', info_user, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('ic', info_chat, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('im', info_message, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('if', info_forward, pass_args = True))
	dp.add_handler(tg_ext.CommandHandler('iF', info_full, pass_args = True))
