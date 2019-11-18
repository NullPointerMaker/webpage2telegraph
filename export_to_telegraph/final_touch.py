#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _copyB
from bs4 import BeautifulSoup

def _finalTouch(soup, url):
	for item in soup.find_all("footer", class_="author-info"):
		for subitem in item.find_all("a"):
			if subitem.text and "英文版" in subitem.text:
				item.replace_with(subitem)
				break
	if 'pride.com' in url:
		for item in soup.find_all('h2'):
			item.parent.parent.insert(0, _copyB(item))
			item.decompose()
	for item in soup.find_all():
		if item.text == 'Follow TranscendingSelf and support their Fundraiser!':
			item.decompose()
	return soup

def _moveHeadPhoto(soup):
	figure = soup.find('figure')
	if not figure:
		return
	html = str(soup)
	pre_content = BeautifulSoup(html[:html.find('<figure')], features="lxml")
	if len(pre_content.text) > 200:
		return
	soup.insert(0, _copyB(figure))
	figure.decompose()


