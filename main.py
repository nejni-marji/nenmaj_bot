#!/usr/bin/env python3
import logging
from os.path import dirname
from sys import argv

import telegram as tg
import telegram.ext as tg_ext

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
import reply
reply.main(dp)
import status
status.main(dp)

# generic
import commands
commands.main(dp)
import text_parse
text_parse.main(dp)
import inline
inline.main(dp)
import convo
convo.main(dp)

# misc
import youtube
youtube.main(dp)

print('Successful start!')

updater.start_polling()
updater.idle()
