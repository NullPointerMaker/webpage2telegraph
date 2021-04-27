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
	'https://freewechat.com/a/MzU0NTEyMjI1Mg==/2247494547/1',
	'https://freewechat.com/a/MzkyOTE2NzE2MA==/2247483780/1',
	'https://freewechat.com/a/MzIyMTc1Nzc2OA==/2247489247/3',
	'https://freewechat.com/a/MzIyMTc1Nzc2OA==/2247488945/3',
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
	album = export_to_telegraph.getAlbum(urls[3])
	album_sender.send_v2(chat, album)

if __name__=='__main__':
	testAlbum()