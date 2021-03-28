#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText, getTitle
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://www.biede.com/bie-girls/pedophilia-social-media/'
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

if __name__=='__main__':
	test()