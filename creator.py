#!/usr/bin/env python3
from os.path import dirname
from os import execl
from time import sleep, time
from datetime import datetime, timedelta
from psutil import cpu_percent, virtual_memory

import telegram as tg
import telegram.ext as tg_ext

myself = int(open(dirname(__file__) + '/private/myself').read())

def bot_reboot(bot, update):
	if not update.message.from_user.id == myself:
		return None
	msg = bot.send_message(update.message.chat_id,
		'Reŝargante...',
	)
	sleep(1)
	data = str(msg.chat_id)
	execl(dirname(__file__) + '/reboot.py', '--', data)

def bot_shutdown(bot, update):
	if not update.message.from_user.id == myself:
		return None
	bot.send_message(update.message.chat_id,
		'Fermante...',
	)
	sleep(1)
	execl(dirname(__file__) + '/shutdown.py', '--')

def bot_usage(bot, update):
	resp = []
	# get ping
	delta = datetime.now() - update.message.date
	resp.append('Ping: ' + str(delta))
	# get uptime
	start = float(open(dirname(__file__) + '/private/start.txt').read())
	date = datetime(1, 1, 1) + timedelta(seconds = time() - start)
	now = datetime.now().strftime('%H:%M:%S')
	days = date.day-1
	hours = date.strftime('%H:%M:%S')
	if days:
		resp.append('Uptime: {}, {} days, {}'.format(now, days, hours))
	else:
		resp.append('Uptime: {}, {}'.format(now, hours))
	# get usage
	cpu = cpu_percent()
	ram = virtual_memory().percent
	resp.append('CPU: %.3f%%' % cpu)
	resp.append('RAM: %.3f%%' % ram)
	# send message
	bot.send_message(update.message.chat_id,
		'\n'.join(resp),
		reply_to_message_id = update.message.message_id,
	)

def bot_leave(bot, update):
	if not update.message.from_user.id == myself:
		return None
	bot.leave_chat(update.message.chat_id)

def main(dp, group):
	for i in [
		tg_ext.CommandHandler('reboot', bot_reboot),
		tg_ext.CommandHandler('shutdown', bot_shutdown),
		tg_ext.CommandHandler('usage', bot_usage),
		tg_ext.CommandHandler('leave', bot_leave),
	]: dp.add_handler(i, group)
