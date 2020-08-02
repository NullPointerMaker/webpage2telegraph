#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText, getTitle
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://mp.weixin.qq.com/s/DRUSUwYhEVgQ5SigoKTEMQ?url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FDRUSUwYhEVgQ5SigoKTEMQ&share_menu=1&sinainternalbrowser=topnav&mid=4532361255722252&luicode=10000011&lfid=1076033524285233&u=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FDRUSUwYhEVgQ5SigoKTEMQ'
]

s = '''
'''

def testExportAllInText():
	soup = BeautifulSoup(s, features="lxml")
	print(exportAllInText(soup))

def testExport():
	for url in urls:
		print('原文：', url)
		r = export(url, True, True, True)
		print('导出：', r)
		os.system('open ' + _formaturl(r) + ' -g')
		print('')

def test():
	testExport()
	# testExportAllInText()

if __name__=='__main__':
	test()