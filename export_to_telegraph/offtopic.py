#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey
from .common import fact, _wrap
from .images import _yieldPossibleImg
import sys

OFFTOPIC_TAG = ['small', 'address', 'meta', 'script']

OFFTOPIC_ATT = [
	'social', 'comment', 'latest', 'widget', 'more', 'button', 'facebook', 
	'cn-carousel-medium-strip', 'video__end-slate__top-wrapper', 'metadata', 
	'el__article--embed', 'signup', 'related', 'disclaimer', 'off-screen', 
	'story-body__unordered-list', 'story-image-copyright', 'article-header', 
	'top-wrapper', 'bottom-of-article', 'bottom-wrapper', 'linkList', 
	'display:none;', 'accordion', 'el-editorial-source', 'video__end-slate__tertiary-title',
	'adblocker', 'tagline', 'navbar', 'navmenu', 'topHeader', 'Post Bottom',
	't_callout', 'add-interest', 'bb-newsletter', 'popover', 'toast', 'after-article', 
	'submeta', 'rich-link__container'
]

OFFTOPIC_CLASSES = ['ads']

DIV_AD_WORDS = [
	'《纽约时报》推出每日中文简报',
	'订阅《纽约时报》中文简报',
]

P_AD_WORDS = [
	'The Times is committed', 
	'Follow The New York Times',
	'Love HuffPost',
]

def _isOffTopic(attrs):
	if not attrs:
		return False
	r = []
	for k, v in attrs.items():
		if matchKey(k, ['href', 'src', 'url', 'alt', 'data']):
			continue
		r.append(str(k) + ' : ' + str(v))
	r = '\n'.join(r)
	if matchKey(r, OFFTOPIC_ATT):
		return True
	if 'sidebar' in r and not matchKey(r, ['no-sidebar']):
		return True
	if 'hidden' in r and not matchKey(r, ['lazy', 'false', 'label-hidden']):
		return True
	if 'copyright' in r and not 'and' in r:
		return True
	return False

def _decompose(item):
	if 'offtopic' in str(sys.argv) and item.text and len(item.text) > 500:
		print('decomposing long text: ', item.attrs)
		if item.name in OFFTOPIC_TAG:
			print(item.name)
		for att in OFFTOPIC_ATT:
			if att in str(item.attrs):
				print(att)
	item.decompose()

def _decompseAds(soup):
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			_decompose(item)
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			_decompose(item)

def _decomposeOfftopic(soup, url):
	for item in soup.find_all():
		if _isOffTopic(item.attrs) or \
			item.name in OFFTOPIC_TAG:
			_decompose(item)

	for c in OFFTOPIC_CLASSES:
		for item in soup.find_all(class_=c):
			_decompose(item)

	if not matchKey(url, ['medium']):
		for item in soup.find_all('h1'):
			_decompose(item)

	_decompseAds(soup)

	for item in soup.find_all("header"):
		s = item.find("p", {"id": "article-summary"})
		img = next(_yieldPossibleImg(item), None)
		if not s or not s.text:
			if img:
				item.replace_with(img)
			else:
				_decompose(item)
			continue
		if not img:
			item.replace_with(s)
			continue
		cap = img.find('figcaption')
		if cap and not cap.text:
			cap.replace_with(_wrap('figcaption', s.text))
			item.replace_with(img)
			continue
		if not cap and img.name in ['div', 'figure']:
			img.append(_wrap('figcaption', s.text))
			item.replace_with(img)
			continue
		item.replace_with(_wrap('p', img, s))
	return soup