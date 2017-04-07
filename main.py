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
import info
info.main(dp)
log_time('info')
import reply
reply.main(dp)
log_time('reply')
import status
status.main(dp)
log_time('status')

# generic
import commands
commands.main(dp)
log_time('commands')
import text_parse
text_parse.main(dp)
log_time('text_parse')
import inline
inline.main(dp)
log_time('inline')
import sock
sock.main(dp)
log_time('sock')

# misc
import youtube
youtube.main(dp)
log_time('youtube')

print('Successful start!')

updater.start_polling()
updater.idle()
