#!/usr/bin/env python3
import re
from os.path import dirname
from glob import glob
from subprocess import call
from os.path import getsize

import telegram as tg
import telegram.ext as tg_ext
import youtube_dl

from bin.background import background

myself = int(open(dirname(__file__) + '/private/myself').read())
yt_dir = dirname(__file__) + '/private/youtube/'

class YouTube():
	def __init__(self, bot, ids, first_name, args, mode, debug = False):
		# head
		self.bot = bot
		self.user_id, self.chat_id, self.message_id = ids
		self.first_name = first_name
		self.mode = mode
		self.debug = debug
		if self.get_video_id(args) == False:
			return None
		self.send_report()
		self.init_info()

		# body
		try:
			if mode == 'audio':
				self.get_video('140', '.m4a')
				self.get_prefix('RAW')
				self.get_mp3('-unedited.mp3')
				self.get_size('-unedited.mp3')
				self.send_audio('-unedited.mp3')
			if mode == 'video':
				self.get_video('18', '.mp4')
				self.get_prefix('RAW')
				#self.get_mp3('.m4a')
				self.get_size('.mp4')
				self.send_video('.mp4')
			if mode == 'nightcore':
				self.get_video('140', '.m4a')
				self.get_prefix('NC')
				self.get_nightcore('-nightcore.mp3')
				self.get_size('-nightcore.mp3')
				self.send_audio('-nightcore.mp3')
			if mode == 'daycore':
				self.get_video('140', '.m4a')
				self.get_prefix('DC')
				self.get_daycore('-daycore.mp3')
				self.get_size('-daycore.mp3')
				self.send_audio('-daycore.mp3')
			if not self.debug:
				self.send_channel()
			self.send_info('Finished', [self.file_name, self.size])
		except:
			self.send_info('Failed', [self.video_id])

	def get_video_id(self, args):
		pat = '((?<=v=)|(?<=youtu\.be\/)|^)[0-9A-Za-z-_]{11}$'
		try:
			self.video_id = re.search(pat, args[0], re.I).group()
			return True
		except:
			return False

	def send_report(self):
		self.bot.send_message(myself, '\n'.join([
			'#ALERT',
			'#{}'.format(self.mode.upper()),
			'*{} ({}) is trying to use your bot to {} a video!*'.format(
				self.first_name,
				self.user_id,
				{
					'audio': 'download the audio from',
					'video': 'download',
					'nightcore': 'make a nightcore of',
					'daycore': 'make a daycore of',
				}[self.mode]
			),
			'The video is: youtu.be/{}'.format(self.video_id),
		]))

	def send_channel(self):
		self.bot.forward_message(
			chat_id = '@nenmaj_cravi',
			from_chat_id = self.chat_id,
			message_id = self.upload_id,
		)

	def init_info(self):
		self.info_id = self.bot.send_message(self.chat_id,
			'Starting process...',
			reply_to_message_id = self.message_id,
		).message_id

	def send_info(self, label, data):
		text = '{}:\n{}'.format(label, '\n'.join(data))
		self.bot.edit_message_text(
			chat_id = self.chat_id,
			message_id = self.info_id,
			text = text
		)

	def ydl(self, video_format):
		ydl_opts = {
			'format': video_format,
			'outtmpl': yt_dir + '%(title)s-%(id)s.%(ext)s',
			'restrictfilenames': True,
		}
		# download video
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([self.video_id])

	def get_size(self, ext):
		size = getsize(yt_dir + self.file_name + ext)
		if size >= 1024:
			size = size/1024
			prefix = 'K'
		if size >= 1024:
			size = size/1024
			prefix = 'M'
		if size >= 1024:
			size = size/1024
			prefix = 'G'
		self.size = '{0:.2f}'.format(size) + ' {}B'.format(prefix)

	def get_prefix(self, prefix):
		self.prefixed = '{}:{}'.format(prefix, self.file_name)

	def get_video(self, num, ext):
		self.send_info('Downloading', [self.video_id])
		path = glob('{}*-{}{}'.format(yt_dir, self.video_id, ext))
		if not path: # call ydl
			self.ydl(num)
		self.file_name = glob('{}*-{}{}'.format(yt_dir, self.video_id, ext))
		self.file_name = self.file_name[0].split('/')
		self.file_name.reverse()
		self.file_name = self.file_name[0][:-4]

	def get_mp3(self, ext):
		self.send_info('Converting to mp3', [self.file_name])
		run  = 'ffmpeg -i {}.m4a '.format(yt_dir + self.file_name)
		run += '-n -loglevel error '
		run += '{}{}'.format(yt_dir + self.file_name, ext)
		call(run, shell = True)

	def get_nightcore(self, ext):
		self.send_info('Nightcoring', [self.file_name])
		run  = 'ffmpeg -i {}.m4a '.format(yt_dir + self.file_name)
		run += '-n -loglevel error '
		run += '-af "asetrate=44100*1.15,atempo=1.05" '
		run += '{}{}'.format(yt_dir + self.file_name, ext)
		call(run, shell = True)

	def get_daycore(self, ext):
		self.send_info('Daycoring', [self.file_name])
		run  = 'ffmpeg -i {}.m4a '.format(yt_dir + self.file_name)
		run += '-n -loglevel error '
		run += '-af "asetrate=44100*0.85,atempo=0.95" '
		run += '{}{}'.format(yt_dir + self.file_name, ext)
		call(run, shell = True)

	def send_audio(self, ext):
		self.send_info('Sending audio', [self.file_name, self.size])
		self.upload_id = self.bot.send_audio(self.chat_id,
			open(yt_dir + self.file_name + ext, 'rb'),
			title = self.prefixed + ext
		).message_id

	def send_video(self, ext):
		self.send_info('Sending video', [self.file_name, self.size])
		self.upload_id = self.bot.send_video(self.chat_id,
			open(yt_dir + self.file_name + ext, 'rb'),
			caption = self.file_name + ext
		).message_id

@background
def youtube_meta(bot, update, args, mode, debug = False):
	ids = [
		update.message.from_user.id,
		update.message.chat_id,
		update.message.message_id,
	]
	first_name = update.message.from_user.first_name
	YouTube(bot, ids, first_name, args, mode, debug = debug)

def youtube_audio(bot, update, args):
	youtube_meta(bot, update, args, 'audio')

def youtube_video(bot, update, args):
	youtube_meta(bot, update, args, 'video')

def youtube_nightcore(bot, update, args):
	youtube_meta(bot, update, args, 'nightcore')

def youtube_daycore(bot, update, args):
	youtube_meta(bot, update, args, 'daycore')

def youtube_debug(bot, update, args):
	mode = args.pop(0)
	youtube_meta(bot, update, args, mode, debug = True)

def main(dp, group):
	for i in [
		tg_ext.CommandHandler('audio', youtube_audio, pass_args = True),
		tg_ext.CommandHandler('video', youtube_video, pass_args = True),
		tg_ext.CommandHandler('nightcore', youtube_nightcore, pass_args = True),
		tg_ext.CommandHandler('daycore', youtube_daycore, pass_args = True),
		tg_ext.CommandHandler('debug', youtube_debug, pass_args = True),
	]: dp.add_handler(i, group)
