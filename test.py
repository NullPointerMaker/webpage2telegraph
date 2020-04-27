#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://mp.weixin.qq.com/s?__biz=MzU4ODM5MDA3OA==&amp;mid=2247493516&amp;idx=2&amp;sn=d6dadcd3267539c176025f87ff6d1d7e&amp;chksm=fddf2c5dcaa8a54b03c5d17fcc35fd81b9b1c45696e1a3e856c1712ee45e1c57a9479dad08db&amp;mpshare=1&amp;scene=1&amp;srcid=0427ORTVRydVaOV2P64wsa5K&amp;sharer_sharetime=1587979114512&amp;sharer_shareid=be2d6afe3d0ef6294408673c30c94f31#rd'
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
		r = export(url, True, True, False)
		print('导出：', r)
		if 'open' in str(sys.argv):
			os.system('open ' + _formaturl(r) + ' -g')
		print('')

def test():
	testExport()
	# testExportAllInText()

if __name__=='__main__':
	test()