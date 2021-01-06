#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webpage2telegraph
from webpage2telegraph import transfer, _formaturl, exportAllInText, getTitle
import os
import sys
from bs4 import BeautifulSoup

urls = [
	'https://photos.google.com/share/AF1QipOtOHHWLLtS9RV6yMuIpT9qpUSnoAv2tRg9OpEH27wkf39qU-cRTpn9uJGOd_FTpw?key=a0k1NHNoYmdvY256Y2oyVWd3aXV1TlNJOUk4Wjl3'
]

s = '''
'''

def testExportAllInText():
	soup = BeautifulSoup(s, features="lxml")
	print(exportAllInText(soup))

def testExport():
	for url in urls:
		# print(webpage2telegraph.getTitle(url))
		print('原文：', url)
		r = webpage2telegraph.transfer(url, True, True, True)
		print('导出：', r)
		os.system('open ' + _formaturl(r) + ' -g')
		print('')

def test():
	testExport()
	# testExportAllInText()

if __name__=='__main__':
	test()