#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://telegra.ph/%E8%A8%98%E8%80%85%E6%89%8B%E8%A8%98%E8%AA%B0%E9%82%84%E6%B2%92%E6%94%B6%E5%88%B0%E7%BE%8E%E5%9C%8B%E6%94%BF%E5%BA%9C%E7%99%BC%E4%BE%86%E7%9A%84%E7%B4%86%E5%9B%B0%E9%87%91-04-23',
]

s = '''
https://telegra.ph/%E8%A8%98%E8%80%85%E6%89%8B%E8%A8%98%E8%AA%B0%E9%82%84%E6%B2%92%E6%94%B6%E5%88%B0%E7%BE%8E%E5%9C%8B%E6%94%BF%E5%BA%9C%E7%99%BC%E4%BE%86%E7%9A%84%E7%B4%86%E5%9B%B0%E9%87%91-04-23 bot_simplify
'''

def testExportAllInText():
	soup = BeautifulSoup(s, features="lxml")
	print(exportAllInText(soup))

def testExport():
	if len(sys.argv) > 1:
		mode = sys.argv[1]
	else:
		mode = ''
	if mode == 'open':
		mode = ''
	for url in urls:
		if not mode in url:
			continue
		print('原文：', url)
		r = export(url, True, True, True)
		print('导出：', r)
		if 'open' in str(sys.argv):
			os.system('open ' + _formaturl(r) + ' -g')
		print('')

def test():
	testExport()
	# testExportAllInText()

if __name__=='__main__':
	test()