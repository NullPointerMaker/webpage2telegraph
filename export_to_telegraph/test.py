#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __init__ import export, _formaturl
import os
import sys

urls = [
	'http://telegra.ph/This-Photographer-Is-Empowering-Trans-Youth-Through-Art-11-17-40',
	'https://www.pride.com/holidays/2018/12/21/7-tips-surviving-holidays-lgbtq-person?utm_source=facebook&utm_medium=social&utm_campaign=holidays&fbclid=IwAR3VT99kqe3S8R8hR6j4qEVVxjBGTMILc0MeuHH2oQFN5hg1LFmdAddfdVU#media-gallery-media-7',
	'https://www.pride.com/art/2018/5/10/photographer-empowering-trans-youth-through-art?fbclid=IwAR1WM82jyIovZRmLQwgJtBTExGGy-_py6SnOirDb2_IEjEAxxzqyKCjqLxY#media-gallery-media-3',
	'https://www.telegraph.co.uk/global-health/women-and-girls/dumped-babies-just-tip-iceberg-deadly-consequences-curbing-reproductive/?fbclid=IwAR0uwFvu3QjbhnYyMxfeN2PtlczcgoiWASrEdRsikQ1Y5TTAO6_PpGH2nDk',
	'https://www.businessinsider.com/trump-other-advertisers-spending-most-on-facebook-political-ads-2019-11?fbclid=IwAR0xfLbdGxBDEBL_WhLQWl8BIUXqEGaw8SP7x6DWSXExClF4x98ZG_w5YCY',
	'https://t.co/k2kLBpdQhl',
	'https://t.co/4ik2VsUHeB',
	'https://edition.cnn.com/2019/11/11/asia/mouse-deer-vietnam-chevrotain-rediscovered-scn/index.html',
	'https://www.pinknews.co.uk/2019/11/14/same-sex-marriage-in-sweden-and-denmark-has-reduced-the-number-of-lesbians-and-gay-men-dying-by-suicide-by-almost-half/?fbclid=IwAR2Rq8aPs7lACGJOmC_N549Px9QvZAYGeCjd8_Z-i5owBlLKbtX7UyGm4l8',
	'https://www.nytimes.com/2019/10/10/opinion/sunday/feminism-lean-in.html',
	'https://gen.medium.com/everyones-missing-the-obvious-when-it-comes-to-the-declining-u-s-birth-rate-679abebb854b',
	'https://mp.weixin.qq.com/s/cJLQFljjbT0NzaiMR801aA',
	'https://cn.nytimes.com/china/20191112/hong-kong-protests-volunteer/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://telegra.ph/%E9%A6%99%E6%B8%AF%E6%8A%97%E8%AE%AE%E8%80%85%E8%83%8C%E5%90%8E%E7%9A%84%E5%BF%97%E6%84%BF%E8%80%85%E5%A4%A7%E5%86%9B-11-16',
	'https://www.idiva.com/news-opinion/womens-issues/transgender-cabbies-who-are-making-indian-roads-safer-for-women/18004255?fbclid=IwAR3aOtNX0fOukmJ-JNJiImobMfPyVhQ63-i5oEUX38_TRlU4-aBLvHwmaA0',
	'https://www.eurekalert.org/pub_releases/2019-11/lu-ada111519.php',
	'bbc.in/2W2Gohc',
	'https://t.co/Joty1jyQwt',
	'https://www.dw.com/zh/%E6%91%A9%E6%A0%B9%E5%A4%A7%E9%80%9A%E4%B8%80%E5%A4%A7%E9%99%86%E7%B1%8D%E5%91%98%E5%B7%A5%E5%9C%A8%E9%A6%99%E6%B8%AF%E9%81%AD%E6%9A%B4%E6%89%93/a-50723184',
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
		r = export(url, True, True)
		print('导出：', r)
		if 'open' in str(sys.argv):
			os.system('open ' + _formaturl(r) + ' -g')
		print('')

_test()