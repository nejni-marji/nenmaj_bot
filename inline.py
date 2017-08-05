#!/usr/bin/env python3
import re
from os.path import dirname
from uuid import uuid4
from random import randint

import telegram as tg
import telegram.ext as tg_ext

from bin.background import background

myself = int(open(dirname(__file__) + '/private/myself').read())

subs_dict = {
	'xxTVT': 'http://tvtropes.org/pmwiki/pmwiki.php',
	'xxLongJBO': 'jbojevysofkemsuzgugje\'ake\'eborkemfaipaltrusi\'oke\'ekemgubyseltru',
	'xxCCCP': '☭',
	'xxLenny': '( ͡° ͜ʖ ͡°)',
	'xxIB': '‽',
	'xxCMD ': '/\xad',
}
subs_re = {}
for sub in subs_dict:
	subs_re[sub] = re.compile(sub)
sub_all = re.compile('|'.join(subs_dict))

def subs_ls(bot, update):
	subs_list = []
	for i in subs_dict:
		subs_list.append('{}: {}'.format(i, subs_dict[i]))
	bot.send_message(update.message.chat_id,
		'\n'.join(subs_list),
		disable_web_page_preview = True
	)

@background
def inlinequery(bot, update):
	inline_query = update.inline_query
	query = update.inline_query.query
	results = list()

	if query:
		# xxSubs
		subs_used = sub_all.findall(query) # list of subs used in query
		text = query
		desc = ', '.join(subs_used)
		for sub in subs_used:
			text = subs_re[sub].sub(subs_dict[sub], text, count = 1)
		if subs_used:
			results.append(tg.InlineQueryResultArticle(id = uuid4(),
				title = 'xxSubs',
				# desc is all instances that were substituted
				description = desc,
				input_message_content = tg.InputTextMessageContent(
					text
				)
			))
		else:
			results.append(tg.InlineQueryResultArticle(id = uuid4(),
				title = '/subs',
				# desc is all instances that were substituted
				description = 'Gives a list of substitutions.',
				input_message_content = tg.InputTextMessageContent(
					'/subs'
				)
			))

	if query:
		# Strike!
		text = '\u0336'.join(list(query)) + '\u0336'
		desc = text
		results.append(tg.InlineQueryResultArticle(id = uuid4(),
			title = 'Strikethrough',
			# desc is all instances that were substituted
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text
			)
		))

	if query:
		# Vaporwave
		text = ''
		for i in list(''.join(query.split())):
			text += chr(0xFEE0 + ord(i))
		#text = ' '.join(list(query))
		desc = text
		results.append(tg.InlineQueryResultArticle(id = uuid4(),
			# seriously, if this is overused, it should be removed # IGNORE THIS LINE
			title = 'Vaporwave',
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text
			)
		))

	if query:
		# Markdown (No Preview)
		text = query
		desc = text
		results.append(tg.InlineQueryResultArticle(id=uuid4(),
			title = 'Markdown (No Preview)',
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text,
				parse_mode = tg.ParseMode.MARKDOWN,
				disable_web_page_preview = True
			)
		))

	if query:
		# Markdown (Preview)
		text = query
		desc = text
		results.append(tg.InlineQueryResultArticle(id=uuid4(),
			title = 'Markdown (Preview)',
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text,
				parse_mode = tg.ParseMode.MARKDOWN,
				disable_web_page_preview = False
			)
		))

	# send inline query results
	bot.answer_inline_query(update.inline_query.id, results, cache_time = 0)

def main(dp):
	dp.add_handler(tg_ext.InlineQueryHandler(inlinequery))
	dp.add_handler(tg_ext.CommandHandler('subs', subs_ls))
