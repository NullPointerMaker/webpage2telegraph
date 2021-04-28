#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText, getTitle
import os
import sys
from bs4 import BeautifulSoup
from telegram.ext import Updater
import album_sender

with open('bot_token') as f:
	bot_token = f.read().strip()
tele = Updater(bot_token, use_context=True)
chat = tele.bot.get_chat(420074357)

urls = [
	'https://freewechat.com/a/MjM5NTg5OTE0NA==/2653691864/1',
]

s = '''
'''

def testExportAllInText():
	soup = BeautifulSoup(s, features="lxml")
	print(exportAllInText(soup))

def testExport():
	for url in urls:
		print(export_to_telegraph.getTitle(url))
		# print('原文：', url)
		# r = export_to_telegraph.export(url, True, True, True)
		# print('导出：', r)
		# os.system('open ' + _formaturl(r) + ' -g')
		# print('')

def test():
	testExport()
	# testExportAllInText()

def testAlbum():
	album = export_to_telegraph.getAlbum(urls[0])
	album_sender.send_v2(chat, album)

if __name__=='__main__':
	testAlbum()