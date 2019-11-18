#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey
from common import fact
from images import _yieldPossibleImg

OFFTOPIC_TAG = ['small', 'address', 'meta', 'script']

OFFTOPIC_ATT = [
	'social', 'comment', 'latest', 'widget', 'more', 'button', 'facebook', 
	'cn-carousel-medium-strip', 'video__end-slate__top-wrapper', 'metadata', 
	'el__article--embed', 'signup', 'related', 'disclaimer', 'off-screen', 
	'story-body__unordered-list', 'story-image-copyright', 'article-header', 
	'top-wrapper', 'bottom-of-article', 'bottom-wrapper', 'linkList', 
	'display:none;', 'accordion', 'el-editorial-source', 'video__end-slate__tertiary-title',
	'adblocker', 'tagline', 'navbar', 'navmenu', 'topHeader'
]

OFFTOPIC_CLASSES = ['ads']

def _isOffTopic(attrs):
	if matchKey(attrs, OFFTOPIC_ATT):
		return True
	if 'sidebar' in attrs and not matchKey(attrs, ['no-sidebar']):
		return True
	if 'hidden' in attrs and not matchKey(attrs, ['lazy', 'false', 'label-hidden']):
		return True
	if 'copyright' in attrs and not 'and' in attrs:
		return True
	return False

DIV_AD_WORDS = [
	'《纽约时报》推出每日中文简报',
	'订阅《纽约时报》中文简报',
]

P_AD_WORDS = [
	'The Times is committed', 
	'Follow The New York Times',
]

def _decompseAds(soup):
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			item.decompose()
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			item.decompose()

def _decomposeOfftopic(soup, url):
	for item in soup.find_all():
		if _isOffTopic(str(item.attrs)) or \
			item.name in OFFTOPIC_TAG:
			item.decompose()

	for c in OFFTOPIC_CLASSES:
		for item in soup.find_all(class_=c):
			item.decompose()

	if not matchKey(url, ['medium']):
		for item in soup.find_all('h1'):
			item.decompose()

	_decompseAds(soup)

	for item in soup.find_all("header"):
		wrapper = fact().new_tag("p")
		s = item.find("p", {"id": "article-summary"})
		img = next(_yieldPossibleImg(item), None)
		if s:
			if not img:
				item.replace_with(s)
				return
			x = fact().new_tag("figcaption")
			x.append(s)
			if img.name in ['div', 'figure']:
				cap = img.find('figcaption')
				if cap and not cap.text:
					cap.replace_with(x)
				elif not cap:
					img.append(x)
				else:
					wrapper.append(s)	
			else:
				wrapper.append(x)
		item.replace_with(wrapper)
	
	return soup