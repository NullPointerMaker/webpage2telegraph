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

def _findFigure(soup, before_content):
	figure = soup.find('figure')
	if figure:
		html = str(soup)
		pre_content = BeautifulSoup(html[:html.find('<figure')], features="lxml")
		if len(pre_content.text) < 200:
			return figure
	if not before_content:
		return 
	before_content = BeautifulSoup(before_content, features="lxml")
	figures = before_content.find_all('figure')
	if len(list(figures)) == 1:
		return figures[0]
	if 'telegraph.co.uk' in str(before_content):
		return figures[-1]

def _moveHeadPhoto(soup, before_content):
	figure = _findFigure(soup, before_content)
	if not figure:
		return
	soup.insert(0, _copyB(figure))
	figure.decompose()


