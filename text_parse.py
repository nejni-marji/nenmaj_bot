#!/usr/bin/env python3
import re
import sqlite3
from os.path import dirname
from random import randint
from itertools import permutations

import telegram as tg
import telegram.ext as tg_ext

from bin.background import background

myself = int(open(dirname(__file__) + '/private/myself').read())

@background
def text_parse(bot, update):
	text = update.message.text
	user = update.message.from_user
	def check_at_bot():
		# This code was moved from bot_personal()
		bot_named = re.search('nenmaj|sampre', text.lower())
		try:
			bot_replied = update.message.reply_to_message.from_user.id == bot.id
		except:
			bot_replied = False
		bot_pm = update.message.chat_id > 0
		at_bot = bot_named or bot_replied or bot_pm
		my_bot = re.search('\\b(m(y|ia) (ro)?boto?|(ro)?boto? mia)\\b', text.lower())
		master = (at_bot or my_bot) and user.id == myself
		# check variables
		return at_bot or master
	def bot_resp(
		# I'll mark where the args and kwargs are.
			pattern,
			response,
			chance = 1,
			call = 'text',
			words = True,
			sub = False,
			markdown = False,
			bot_kwargs = {}
		):

		call_list = { # kwarg: call
			'text': bot.send_message,
			'photo': bot.send_photo,
			'document': bot.send_document,
			'sticker': bot.send_sticker,
		}

		match = re.search(pattern, text, flags = re.I) # arg: pattern

		if words: # kwarg: words
			pattern = '\\b(%s)\\b' % pattern # arg: pattern

		if sub: # kwarg: sub
			subs = re.sub(pattern, response, text, flags = re.I)
			if subs:
				response = subs + '*'

		match = re.search(pattern, text, flags = re.I) # arg: pattern

		bot_kwargs['reply_to_message_id'] = update.message.message_id
		bot_kwargs['parse_mode'] = tg.ParseMode.MARKDOWN
		if not markdown:
			bot_kwargs.pop('parse_mode')

		# set bob
		if update.message.from_user.id == myself:
			bob = update.message.from_user.first_name
		else:
			bob = 'Bob'

		is_pm = update.message.chat_id > 0
		if match and (randint(1, chance) == 1 or is_pm or check_at_bot()): # kwarg: chance
			response = response.format( # arg: response
				text = update.message.text,
				match = match.group(),
				match_lower = match.group().lower(),
				match_upper = match.group().upper(),
				match_capitalize = match.group().capitalize(),
				username = update.message.from_user.username,
				first_name = update.message.from_user.first_name,
				last_name = update.message.from_user.last_name,
				bob = bob,
			)

			return call_list[call]( # kwarg: call
				update.message.chat_id,
				response, # arg: response
				**bot_kwargs # kwarg: bot_kwargs
			)

		else:
			return False
	def bot_special():
		# I'm moving all the stuff that was in bot_response to here for the time being.
		hacker_list = [
			'AgADAwADr6cxG3g0AUwoHebva7LgVtLkhjEABHBt9cFF3a_w9YAAAgI',
			'AgADAwADsKcxG3g0AUypcvpgwOzxUPpZljEABATMDotf2VIY8zQAAgI',
			'AgADAwADsacxG3g0AUxAI_atJuFs1XNeljEABAkoj9oSW_fWMzQAAgI',
			'AgADAwADsqcxG3g0AUx7Yyv0pQnWhnkHhzEABOkUTQABsNf0ylpMAAIC',
			'AgADAwADs6cxG3g0AUwODkvMlyjxKwblhjEABKUfPy2Eg0zVRHkAAgI',
			'AgADAwADtKcxG3g0AUzdKpQ7CrMq5J_ihjEABJwt-PN5TxUUR3UAAgI',
			'AgADAwADtacxG3g0AUyezs82Afs3i_3phjEABCLZZcZcEvp3T3kAAgI',
			'AgADAwADtqcxG3g0AUyvYVfDUd1-mbsFhzEABBtrwmhgNUqh_UwAAgI',
			'AgADAwADt6cxG3g0AUzzcit_ZZryBOHqhjEABD8_RvXXQZfFSHUAAgI',
			'AgADAwADuKcxG3g0AUwFJcO3pDOy3c3phjEABIG7x7ZJzHci_3YAAgI',
			'AgADAwADuacxG3g0AUzhQwN3RUqIZmpWljEABNLkOs2zLQ_0OTMAAgI',
		]
		hacker = hacker_list[randint(0, len(hacker_list) - 1)]
		bot_resp(
			'(net)?h[a4](ck|x$|xx+)([o0e3]r)?[sz]*(e3d)?(net)?',
			hacker,
			call = 'photo',
		)
		if check_at_bot():
			for i in permutations(['mi', 'amas', 'vin']):
				bot_resp(
					' '.join(i),
					'Kaj ankaŭ {match_lower}, {first_name}!',
				)
	def bot_responses():
		# This is a goddammed massterpiece. Don't ever change, nenmaj.
		if True: # general commands
			bot_resp(
				"#poste",
				"mdr, ĉu vere?",
				words = False,
			)
			bot_resp(
				"fuck me",
				"_Later, okay?_",
				chance = 5,
				markdown = 1,
			)
			bot_resp(
				"furz",
				"CgADAwADAgAD1a5dESoG4V8v7zq2Ag",
				chance = 5,
				call = 'document',
				words = False,
			)
			bot_resp(
				"(^|>)implying\b",
				"AgADBAADOHY2G4wXZAep1wim0UXDiOtgoBkABA2QViTh4nAECDUBAAEC",
				call = 'photo',
				words = False,
			)
			bot_resp(
				"spicy memes?",
				"AgADBAADopI1G2gbZAcZhRV15auVr1VcYRkABPSZqMh9ovzsmbYCAAEC",
				chance = 5,
				call = 'photo',
			)
			bot_resp(
				"anthony",
				"_I gotta have that big dick of yours!_",
				chance = 25,
				markdown = 1,
			)
			bot_resp(
				"sorry about that",
				"AgADAwADWL4xGyR2xAWxxoMBi_TiBGzuhjEABCTgEwGw_lZrnXQAAgI",
				call = 'photo',
			)
			bot_resp(
				"horsecock",
				"AgADAQADsqcxG-ba8EQwAcblg5EzOd0k7y8ABEeChQibvySCWSwAAgI",
				call = 'photo',
			)
			bot_resp(
				"who y(a|ou?) gonna call",
				"AgADAwADqacxG3rvQE9sl7ujoxSKl0_4hjEABJZ2Tr5bRwn5M_8AAgI",
				call = "photo",
			)
			bot_resp(
				"damn?[.,? s[uo]n",
				"AgADAwADm74xGyR2xAWmtgzaV8M5UsnthjEABEQb0R-YkV5X5ncAAgI",
				call = 'photo',
			)
			bot_resp(
				"ding d(ing d|ong s)ong|my tra la la",
				"https://youtu.be/z13qnzUQwuI",
				markdown = 1,
			)
			bot_resp(
				"sponge ?bob|square ?pants",
				"I think the funny part was\nWith SpongeBob was just sigen\nOUT of nowhere\nAnd squeaked word was like\ncan't BELIEVE IT",
				chance = 5,
			)
			bot_resp(
				"fuck th[ea] police",
				"_Comin' straight from the underground_",
				markdown = 1,
			)
			bot_resp(
				"#1\b|\bwe are (number (one|#?1)|#1)\b",
				"https://youtu.be/PfYnvDL0Qcw",
				chance = 5,
				words = False,
			)
			bot_resp(
				"pizza hut|taco bell",
				"http://youtu.be/EQ8ViYIeH04",
				markdown = True,
			)
			bot_resp(
				"meme",
				"CAADAQADQwEAAuUjAgZ13bKfyZHk7AI",
				chance = 10,
				call = 'sticker',
				words = False,
			)
			bot_resp(
				"^same( \w+)?$",
				"same",
				chance = 10,
			)
			bot_resp(
				"magick?s?",
				"BQADBAADLQkAAjEdZAeWrM9ia4ld6gI",
				call = 'document',
			)
			bot_resp(
				"(the )?batman",
				"a man dressed like a bat",
				sub = True,
			)
			bot_resp(
				"(the )?batmen",
				"some men dressed like bats",
				sub = True,
			)
			bot_resp(
				"jesus (fucking|effing) christ",
				"Looks more like Jesus fucking Noah.",
			)
			bot_resp(
				"ready",
				"_Mom's spaghetti~_",
				chance = 5,
				markdown = True,
			)
			bot_resp(
				'animes?',
				'*PURGE THE WEEBS!*',
				chance = 5,
				markdown = True,
			)
			bot_resp(
				"skype",
				"http://stallman.org/skype.html",
			)
			bot_resp(
				"^technically",
				"https://www.xkcd.com/1475/",
				chance = 1,
				words = False,
			)
			bot_resp(
				"wat",
				"AgADBAADYiY1G0UZZAdC3oqoZ4hwJhFXYRkABEJYCrUC4vLTNvABAAEC",
				chance = 5,
				call = 'photo',
			)
			bot_resp(
				"hot sec",
				"hot sex",
				chance = 5,
				sub = True,
			)
			bot_resp(
				"aesthetic",
				"ａｅｓｔｈｅｔｉｃ",
				chance = 5,
			)
			bot_resp(
				"fek al mi",
				"Ja, fek al vi!",
				chance = 5,
			)
			bot_resp(
				"id(ist)?(oj?|s)?",
				"Fekacho a vu!",
				chance = 5,
			)
			bot_resp(
				"a?(l[eou]l|kek)[sz]?",
				"[IF YOU LIKE TO {match_upper}, CHECK OUT JAKE H ON YOUTUBE!](https://www.youtube.com/channel/UCgYTmlAedgFze6SGGGvXG2A)",
				chance = 25,
				markdown = True,
				bot_kwargs = {'disable_web_page_preview': 1},
			)
			bot_resp(
				"mdr",
				"[SE VI ŜATAS MDR-I, RIGARDU JE JAKE H ĈE JUTUBO!](https://www.youtube.com/channel/UCgYTmlAedgFze6SGGGvXG2A)",
				chance = 25,
				markdown = True,
				bot_kwargs = {'disable_web_page_preview': 1},
			)
		if check_at_bot():
			bot_resp(
				'saluton',
				'Resaluton, {first_name}!',
			)
			bot_resp(
				'sal',
				'Resal, {first_name}!',
			)
			bot_resp(
				'bo(vin|n((eg)?an ?)?(m(aten|oment|am)|vesper|nokt(mez)?|'
				+ '(post(?=...mez))?t(emp|ag(er|mez)?)))(eg)?on',
				'Kaj {match_lower} al vi, {first_name}!',
			)
			bot_resp(
				'dank(eg)?on',
				'Nedankinde, {first_name}!',
			)
			bot_resp(
				'hej',
				'Kion vi volas, {first_name}?',
			)
			bot_resp(
				'fek al (vi|nenmaj)|(vi|nenmaj) (estas stulta|stultas)',
				'Bonvole pardonu min, mi estas nur roboto!',
			)
			bot_resp(
				'ŝ+|(kviet|silent|ferm)iĝu',
				'Vi ne povas kvietigi min!',
			)
			bot_resp(
				'h(eyo?|ello|a?i|owdy)|yo|oi|greetings|sup|'
				+ 'good ((eve|mor)ning|day|afternoon)',
				'{match_capitalize}, {first_name}!',
			)
			bot_resp(
				'thanks',
				'No prob, {bob}!',
			)
			bot_resp(
				'i love (you|nenmaj)|ily|(you|nenmaj) is( the)? best (ro)?bot',
				'>///< senpai noticed me!',
			)
			bot_resp(
				'fuc?k (off|(yo)?u)|i hate (yo)?u|sod off|'
				+ 'you(\'?re? (dumb?|stupid)| suck)',
				'Please forgive me, I\'m only a bot!',
			)
			bot_resp(
				's+h+|be (quie|silen)t|shut up',
				'You can\'t tell me to be quiet!',
			)
			bot_resp(
				'rude|rood|r00d|lewd|lood',
				'I\'m a rude dude, and I\'m rather lewd.',
			)
		elif not check_at_bot():
			sal_list = ['sal', 'saluton', 'resal']
			sal = sal_list[randint(0, len(sal_list) - 1)].capitalize()
			bot_resp(
				'sal(uton)?( al|,?) (vi )?(c[hx]|ĉ)iuj?( vi)?',
				sal + ', {first_name}!',
				chance = 5,
			)
			bot_resp(
				'fek al vi',
				'fek a vu',
				chance = 5,
				sub = True,
			)
			hello_list = ['hi', 'hello', 'hey', 'heyo']
			hello = hello_list[randint(0, len(hello_list) - 1)].capitalize()
			bot_resp(
				'h(i|ello|eyo?),? ((y\'?)?all|everyone|people|ppl)',
				hello + ', {first_name}!',
			)
	def bot_ayylmao():
		# Don't do anything if @theayybot is present.
		try:
			theayybot = bot.get_chat_member(update.message.chat_id,
				139464619
			)
			if theayybot.status == 'member':
				return None
		except:
			pass

		res_ayy = re.search('\\b(ayy+)\\b', text.lower())
		res_lmao = re.search('\\b(lmao+)\\b', text.lower())

		if res_ayy and res_lmao:
			resp = 'ayy lmao'
		elif res_ayy:
			resp = 'lmao' + 'o' * len(res_ayy.group()[3:])
		elif res_lmao:
			resp = 'ayy' + 'y' * len(res_lmao.group()[4:])
		if res_ayy or res_lmao:
			bot.send_message(update.message.chat_id,
				resp,
			)
	def bot_reverse():
		# This should be rare. Feel free to change based on chat activity.
		if randint(1, 100) == 1 and not ' ' in text:
			txet = list(text)
			txet.reverse()
			txet = ''.join(txet)
			bot.send_message(update.message.chat_id,
				txet,
				reply_to_message_id = update.message.message_id,
			)
	def bot_motd():
		# Here there be dragons. Those dragons be SQL statements.
		if update.message.message_id % 500 == 0:
			conn = sqlite3.connect(dirname(__file__) + '/private/chats.db')
			data = {'chat_id': update.message.chat_id}
			# SQL SELECT
			resp = 'MOTD:\n' + conn.execute(
				'SELECT message FROM motd\n'
				+ 'WHERE chat_id = :chat_id',
				data
			).fetchone()[0]
			conn.close()
			if resp == None:
				resp = 'MOTD is not set.'
			else:
				bot.send_message(update.message.chat_id,
					resp,
				)
	bot_special()
	bot_responses()
	bot_ayylmao()
	bot_reverse()
	bot_motd()

def main(dp):
	dp.add_handler(tg_ext.MessageHandler(tg_ext.Filters.text, text_parse))
