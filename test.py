#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import export_to_telegraph
from export_to_telegraph import export, _formaturl
import os
import sys

urls = [
	'https://telegra.ph/%E6%99%9A%E5%A0%B1%E6%84%8F%E5%AA%92%E6%89%B9%E4%B8%AD%E5%9C%8B%E5%A4%96%E4%BA%A4%E9%83%A8%E5%82%B3%E6%92%AD%E5%81%87%E6%96%B0%E8%81%9E%E5%8F%A6%E6%8C%87%E4%B8%AD%E5%9C%8B%E6%8D%90%E8%B4%88%E7%89%A9%E8%B3%87%E5%AF%A6%E7%82%BA%E6%84%8F%E5%9C%8B%E8%B3%BC%E7%89%A9%E5%95%86%E5%93%81-03-17-2'
]

def _test():
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

if __name__=='__main__':
	_test()