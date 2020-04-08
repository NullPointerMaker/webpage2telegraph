#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl, exportAllInText
import os
import sys
from bs4 import BeautifulSoup

urls = [
]

s = '''
<blockquote>
<p>【经典老片中字洗版】《#<a href="https://www.douban.com/update/topic/影子部队">影子部队</a>#》（1969）
#<a href="https://www.douban.com/update/topic/让·皮埃尔·梅尔维尔">让·皮埃尔·梅尔维尔</a># 晚期力作，《视与听》影史250佳，关于二战抵抗运动题材的影史最佳之一！
此前网络上的字幕存在不少漏译、误译，时间轴也存在问题，我已在精校与修订翻译之余一并修正，匹配CC蓝光。</p>
</blockquote>
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
	testExportAllInText()

if __name__=='__main__':
	test()