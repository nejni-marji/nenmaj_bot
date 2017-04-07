#!/usr/bin/env python3
import logging
from os.path import dirname
from sys import argv
from time import time

import telegram as tg
import telegram.ext as tg_ext

start = float(open(dirname(__file__) + '/private/start.txt').read())
def log_time(text):
	print('[{:12.6f}] {}'.format(time() - start, text))
log_time('start')

f = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format = f, level=logging.INFO)

logger = logging.getLogger(__name__)

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

token = open(dirname(__file__) + '/private/token.txt').read()
updater = tg_ext.Updater((token))
dp = updater.dispatcher
dp.add_error_handler(error)

try:
	data = [str(argv[1]), str(argv[2])]
	updater.bot.send_message(
		data[0],
		'Mi revenas~!',
		#reply_to_message_id = data[1],
	)
except:
	pass

# utils
for i in [
	'info',
	'reply',
	'status',
	'commands',
	'text_parse',
	'inline',
	'sock',
	'youtube',
]:
	exec('import %s' % i)
	exec('%s.main(dp)' % i)
	exec('log_time(\'%s\')' % i)

print('Successful start!')

updater.start_polling()
updater.idle()
