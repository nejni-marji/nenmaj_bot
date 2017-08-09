#!/usr/bin/env python3
import re
from os.path import dirname
from json import loads
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

# espdic vortaro search
espdic = loads(open(dirname(__file__) + '/private/espdic.json').read())['vortaro']
espdic_en = [i['en'] for i in espdic]

def get_eo(query):
	xsys_list = [
		['cx', 'ĉ'], ['cX', 'ĉ'], ['Cx', 'Ĉ'], ['CX', 'Ĉ'],
		['gx', 'ĝ'], ['gX', 'ĝ'], ['Gx', 'Ĝ'], ['GX', 'Ĝ'],
		['hx', 'ĥ'], ['hX', 'ĥ'], ['Hx', 'Ĥ'], ['HX', 'Ĥ'],
		['jx', 'ĵ'], ['jX', 'ĵ'], ['Jx', 'Ĵ'], ['JX', 'Ĵ'],
		['sx', 'ŝ'], ['sX', 'ŝ'], ['Sx', 'Ŝ'], ['SX', 'Ŝ'],
		['ux', 'ŭ'], ['uX', 'ŭ'], ['Ux', 'Ŭ'], ['UX', 'Ŭ'],
	]
	for xsys in xsys_list:
		pattern, repl = xsys
		query = re.sub(pattern, repl, query)

	suffix_list = [
		['as',  'i'],
		['os',  'i'],
		['is',  'i'],
		['us',  'i'],
		['u',   'i'],
		['oj',  'o'],
		['on',  'o'],
		['ojn', 'o'],
		['aj',  'a'],
		['an',  'a'],
		['ajn', 'a'],
		['en',  'e'],
	]
	for suffix in suffix_list:
		if query.endswith(suffix[0]):
			true_len = len(query) - len(suffix[0])
			query_root = query[:true_len] + suffix[1]
			suffixed = True
			break
		else:
			query_root = query
			suffixed = False

	if not query in espdic_en:
		query = query_root

	return query

def get_en(query):
	if query.startswith('to '):
		query = query[3:]
	return query

def eo_exact(query, entry):
	return query.lower() == entry['eo'].lower()

def en_exact(query, entry):
	regex = '^(to )?' + query + '( \([^)]+\))?$'
	return any([re.match(regex, i, flags = 2) for i in entry['en'].split(', ')])

def eo_fuzzy(query, entry):
	return query.lower() in entry['eo'].lower()

def en_fuzzy(query, entry):
	return any([query.lower() in i.lower() for i in entry['en'].split(', ')])

def search_espdic(query):
	eo = get_eo(query)
	en = get_en(query)

	exact = [i for i in espdic if eo_exact(eo, i) or en_exact(en, i)]
	fuzzy = [i for i in espdic if eo_fuzzy(eo, i) or en_fuzzy(en, i)]

	[fuzzy.remove(i) for i in exact]
	return [exact, fuzzy]

strike = re.compile('<s>(.(?!</s>))+.</s>')
def strike_text(text):
	match = strike.search(text)
	while match:
		text = text.replace(
			match.group(),
			'\u0336'.join(list(match.group()[3:-4])) + '\u0336',
			1
		)
		match = strike.search(text)
	return text

@background
def inlinequery(bot, update):
	inline_query = update.inline_query
	query = update.inline_query.query
	results = list()

	def subs():
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

	def strikethrough():
		text = strike_text(query)
		desc = text
		results.append(tg.InlineQueryResultArticle(id = uuid4(),
			title = 'Strikethrough',
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text,
				parse_mode = tg.ParseMode.MARKDOWN
			)
		))

	def vaporwave():
		text = ''
		for i in list(query):
			text += chr(0xFEE0 + ord(i))
		desc = text
		results.append(tg.InlineQueryResultArticle(id = uuid4(),
			# seriously, if this is overused, it should be removed # IGNORE THIS LINE
			title = 'Vaporwave',
			description = desc,
			input_message_content = tg.InputTextMessageContent(
				text
			)
		))

	def markdown_noprev():
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

	def markdown_prev():
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

	def vortaro():
		nonlocal query
		nonlocal results
		if query:
			if query.startswith('v: '):
				query = query[3:]
				matches = search_espdic(query)

			if 'matches' in locals():
				exact, fuzzy = matches
				matches = exact + fuzzy
				matches = matches[:tg.constants.MAX_INLINE_QUERY_RESULTS]

				# reset results to only show dictionary entries
				results = list()

				for match in matches:
					results.append(tg.InlineQueryResultArticle(id=uuid4(),
						title = match['eo'],
						description = match['en'],
						input_message_content = tg.InputTextMessageContent(
							'*{}*: _{}_'.format(match['eo'], match['en']),
							parse_mode = tg.ParseMode.MARKDOWN
						)
					))
		if not 'matches' in locals() or not matches:
			usage = [
				'Por serĉi la Esperanto-angla vortaro: `v: <vorto>`',
				'To search the Esperanto-English dictionary: `v: <vorto>`',
				'Iksa sistemo uzeblas. / X-system is usable.',
			]
			results.append(tg.InlineQueryResultArticle(id=uuid4(),
				title = 'Vortaro / Dictionary',
				description = 'v: <vorto | word>',
				input_message_content = tg.InputTextMessageContent(
					'\n'.join(usage),
					parse_mode = tg.ParseMode.MARKDOWN
				)
			))

	if query:
		subs()
		strikethrough()
		vaporwave()
		markdown_noprev()
		markdown_prev()
	vortaro()

	# send inline query results
	bot.answer_inline_query(update.inline_query.id, results, cache_time = 0)

def main(dp, group):
	for i in [
		tg_ext.InlineQueryHandler(inlinequery),
		tg_ext.CommandHandler('subs', subs_ls),
	]: dp.add_handler(i, group)
