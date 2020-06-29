#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://squatting2047.com/%e3%80%8c%e4%b8%8d%e7%ae%a1%e4%bd%a0%e6%98%af%e5%90%a6%e5%8f%ab%e6%88%91%e5%80%91%e5%81%9a%e9%a6%99%e6%b8%af%e4%ba%ba%ef%bc%8c%e6%88%91%e5%80%91%e9%83%bd%e6%98%af%e9%a6%99%e6%b8%af%e7%9a%84%e4%b8%80'
]

s = '''
'''

def testExportAllInText():
	soup = BeautifulSoup(s, features="lxml")
	print(exportAllInText(soup))

def testExport():
	if len(sys.argv) > 1:
		mode = sys.argv[1]
	else:
		mode = ''
	if mode in ['open', 'debug']:
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