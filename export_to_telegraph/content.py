#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common import _findRawContent
from bs4 import BeautifulSoup
from telegram_util import matchKey
import sys
from images import _cleanupImages
from common import _copyB, fact
from link import _replaceOfftopicLink
from offtopic import _decomposeOfftopic

DIV_AD_WORDS = [
	'《纽约时报》推出每日中文简报',
	'订阅《纽约时报》中文简报',
]

P_AD_WORDS = [
	'The Times is committed', 
	'Follow The New York Times',
]

def _tagReplace(soup):
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			item.decompose()
			continue
		wrapper = fact().new_tag("p")
		wrapper.append(BeautifulSoup(str(item), features="lxml"))
		item.replace_with(wrapper)
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			item.decompose()
	for section in soup.find_all("section"):
		b = fact().new_tag("p")
		b.append(BeautifulSoup(str(section), features="lxml"))
		section.replace_with(b)
	to_remove_tags = [
		soup.find_all("li"),
		soup.find_all("ul")
	]
	for l in to_remove_tags:
		for item in l:
			new_item = fact().new_tag("p")
			for x in item.find_all(recursive=False):
				new_item.append(x)
			item.replace_with(new_item)
	return soup

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
		if item.text == 'Follow  and !':
			item.decompose()
	return soup

def saveSoup(soup, stage):
	if 'debug' in str(sys.argv):
		with open("tmp_%d.html" % stage, 'w') as f:
			f.write(str(soup))

def _findMainFromSoup(soup, url):
	saveSoup(soup, 0)
	soup = _replaceOfftopicLink(soup)
	saveSoup(soup, 1)
	soup = _decomposeOfftopic(soup, url)
	saveSoup(soup, 2)
	soup = _cleanupImages(soup, url)
	saveSoup(soup, 3)
	soup = _getInnerArticle(soup)
	saveSoup(soup, 4)
	soup = _tagReplace(soup)
	saveSoup(soup, 5)
	soup = _finalTouch(soup, url)
	saveSoup(soup, 6)
	return soup

def _findMain(soup, doc, url):
	result = _findMainFromSoup(soup, url)
	if result:
		return result
	result = _findMainFromSoup(BeautifulSoup(doc.content), url)
	if result:
		return result
	return doc.content()