#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from .common import fact, _copyB
from telegram_util import matchKey

def _getCaption(item):
	if not item:
		return
	for x in item.find_all():
		if 'caption' in str(x.attrs).lower():
			caption = fact().new_tag("figcaption")
			caption.append(_copyB(x))
			return caption

def _formatImgUrl(raw, domain):
	parts = raw.split('/')
	success = False
	for index, part in enumerate(parts):
		if part == 'max':
			try:
				if int(parts[index + 1]) > 0:
					success = True
					break
			except:
				pass
	if success and 'guim' not in raw:
		parts[index + 1] = '1300'
	raw = '/'.join(parts)
	if not matchKey(raw, ['guim']):
		raw = re.sub('width=\d\d*', 'width=1300', raw)
	if matchKey(raw, ['condecdn']):
		raw = re.sub('/\d\d*/', '/1300/', raw)
	if raw.startswith('//'):
		return 'https:' + raw
	if raw.startswith('/'):
		return domain + raw
	return raw

MORE_CERTAIN_IMG_ATTRS = ['data-src-large', 'data-src']
IMG_ATTRS = MORE_CERTAIN_IMG_ATTRS + ['src'] # people would put junk in src field

def _getImgInsideFigure(figure, domain):
	for raw_img in figure.find_all():
		for attr in IMG_ATTRS:
			if raw_img.get(attr):
				r = fact().new_tag("img", src = _formatImgUrl(raw_img[attr], domain))
				if raw_img.get('title'):
					r['title'] = raw_img.get('title')
				return r
	figure.decompose()

def _cleanupFigure(figure, domain):
	iframe = figure.find('iframe')
	if iframe:
		r = fact().new_tag("iframe", src = _formatImgUrl(iframe['src'], domain))
		iframe.replace_with(r)
		return figure
	img = _getImgInsideFigure(figure, domain)
	if not img:
		return
	caption = figure.find('figcaption')
	if not caption and img.get('title'):
		caption = fact().new_tag("figcaption")
		caption.append(img['title'])
	new_figure = fact().new_tag("figure")
	new_figure.append(img)
	if caption:
		new_figure.append(caption)
	for cite in new_figure.find_all('cite'):
		cite.decompose()
	return new_figure

def _findnoscriptImg(img):
	if not img.parent or len(str(img.parent)) > 1000 or \
		len(list(img.parent.find_all('img'))) > 2:
		return
	if img.attrs and set(MORE_CERTAIN_IMG_ATTRS).intersection(set(img.attrs.keys())):
		return
	noscript = img.parent.find('noscript')
	if not noscript:
		return
	return noscript.find('img')

def _yieldPossibleImg(soup):
	possibles = [
		soup.find_all("div", class_="js-delayed-image-load"),
		soup.find_all("figure"),
		soup.find_all("img"),
	]
	for l in possibles:
		for x in l:
			yield x

def _cleanupImages(soup, domain):
	for img in soup.find_all("div", class_="js-delayed-image-load"):
		img.name = 'img'
	
	for img in soup.find_all('img'):
		noscript_img = _findnoscriptImg(img)
		if noscript_img:
			img.replace_with(noscript_img)

	for item in soup.find_all('noscript'):
		item.decompose()

	for figure in soup.find_all('figure'):
		r = _cleanupFigure(figure, domain)
		if r: 
			figure.replace_with(r)
		else:
			figure.decompose()

	for img in soup.find_all('img'):
		if img.parent and img.parent.name == 'figure':
			continue
		if not img.parent:
			img.decompose()
			continue
		caption = _getCaption(img.parent)
		figure = fact().new_tag("figure")
		figure.append(_copyB(img))
		
		if caption:
			figure.append(_copyB(caption))
			caption.decompose()
		r = _cleanupFigure(figure, domain)
		if r: 
			img.replace_with(r)
		else:
			img.decompose()
	return soup