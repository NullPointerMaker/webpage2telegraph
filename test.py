#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webpage2telegraph
from webpage2telegraph import _format_url
import os

urls = [
	'https://photos.google.com/share/AF1QipOtOHHWLLtS9RV6yMuIpT9qpUSnoAv2tRg9OpEH27wkf39qU-cRTpn9uJGOd_FTpw?key=a0k1NHNoYmdvY256Y2oyVWd3aXV1TlNJOUk4Wjl3'
]


def test():
	for url in urls:
		# print(webpage2telegraph.get_title(url))
		print('原文：', url)
		r = webpage2telegraph.transfer(url, True, True, True)
		print('导出：', r)
		os.system('open ' + _format_url(r) + ' -g')
		print('')


if __name__ == '__main__':
	test()
