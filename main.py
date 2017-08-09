#!/usr/bin/env python3
import logging
import importlib
from os.path import dirname
from sys import argv
from time import time

import telegram as tg
import telegram.ext as tg_ext

myself = int(open(dirname(__file__) + '/private/myself').read())

start = float(open(dirname(__file__) + '/private/start.txt').read())
def log_time(text):
	print('[{:12.6f}] {}'.format(time() - start, text))
log_time('imported python libraries')

f = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format = f, level=logging.INFO)

logger = logging.getLogger(__name__)

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

token = open(dirname(__file__) + '/private/token.txt').read()
updater = tg_ext.Updater((token))
dp = updater.dispatcher
dp.add_error_handler(error)

log_time('beginning to import bot modules')

modules = [
	'info',
	'settings',
	'creator',
	'reply',
	'status',
	'commands',
	'text_parse',
	'inline',
	'sock',
	'xkcd',
	'youtube',
	'questions',
]
for i in enumerate(modules):
	group = i[0] + 1
	module = i[1]
	exec('import %s' % module)
	exec('%s.main(dp, %s)' % (module, group))
	log_time('loaded %s.py' % module)

def reload_meta(bot, update, args):
	if not args or not update.message.from_user.id == myself:
		return None
	if args[0] in modules:
		group = [
			i[0] for i in enumerate(modules)
			if args and args[0] == i[1]
		][0]
		module = modules[group]
		reload_module(bot, update, group + 1, module)
	elif args[0] == 'all':
		for i in enumerate(modules):
			reload_module(bot, update, i[0] + 1, i[1])
		reload_message = bot.send_message(
			update.message.chat_id,
			'`Done.`',
			parse_mode = tg.ParseMode.MARKDOWN
		)

def reload_module(bot, update, group, module):
	reload_message = bot.send_message(
		update.message.chat_id,
		'`Reloading %s.py`' % module,
		parse_mode = tg.ParseMode.MARKDOWN
	)

	try:
		del dp.handlers[group]
		dp.groups.remove(group)

		exec('importlib.reload(%s)' % module)
		exec('%s.main(dp, %s)' % (module, group))

		bot.edit_message_text(
			chat_id = update.message.chat_id,
			message_id = reload_message.message_id,
			text = '`Reloaded %s.py`' % module,
			parse_mode = tg.ParseMode.MARKDOWN
		)

	except:
		bot.edit_message_text(
			chat_id = update.message.chat_id,
			message_id = reload_message.message_id,
			text = '`Failed to reload %s.py`' % module,
			parse_mode = tg.ParseMode.MARKDOWN
		)

dp.add_handler(tg_ext.CommandHandler('reload', reload_meta, pass_args = True))
log_time('loaded reloader')

log_time('all modules loaded')

try:
	data = str(argv[1])
	updater.bot.send_message(
		data,
		'Mi revenas~!',
	)
except:
	pass

updater.start_polling()
updater.idle()
