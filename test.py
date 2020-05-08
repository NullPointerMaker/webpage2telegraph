#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://mp.weixin.qq.com/s?__biz=MzIzMTg5MjM2Nw==&amp;mid=2247593091&amp;idx=1&amp;sn=574bdd2d8c91756fa2370a42df0412fa&amp;chksm=e89e1863dfe991759334dc739d9dd8af33cae8977dcc787f4fb8697be810b4a83b997dff4ddf&amp;mpshare=1&amp;scene=1&amp;srcid=&amp;sharer_sharetime=1588263675257&amp;sharer_shareid=ac6cbafa374000428a0e58fcfb7c4b29#rd'
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