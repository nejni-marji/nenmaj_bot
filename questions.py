#!/usr/bin/env python3
from os.path import dirname
from json import loads
from random import randint

import telegram as tg
import telegram.ext as tg_ext

import bin.database as db
from bin.config import configs, check_conf

questions = loads(open(dirname(__file__) + '/private/questions.json').read())

def queue_question(bot, update, job_queue, chat_data):
	name = 'question' + str(update.message.chat_id)
	if name in chat_data:
		chat_data[name].schedule_removal()
	if not check_conf(
		str(update.message.chat_id) + '.questions.enabled',
		bool, False
	):
		return None
	chat_data[name] = job_queue.run_repeating(
		callback = send_question,
		interval = check_conf(
			str(update.message.chat_id) + '.questions.timer',
			int, 60 * 60
		),
		context = update.message.chat_id,
		name = name,
	)

def send_question(bot, job):
	question = questions[randint(0, len(questions) - 1)]
	bot.send_message(
		job.context,
		question,
	)

def main(dp):
	for chat_id in [i for i in configs if check_conf(i + '.questions.enabled', bool, False)]:
		name = 'question' + chat_id
		dp.chat_data[int(chat_id)][name] = dp.job_queue.run_repeating(
			callback = send_question,
			interval = check_conf(chat_id + '.questions.timer', int, 60 * 60),
			context = chat_id,
			name = name,
		)

	dp.add_handler(tg_ext.MessageHandler(tg_ext.Filters.all, queue_question, pass_job_queue = True, pass_chat_data = True), group = 3)
