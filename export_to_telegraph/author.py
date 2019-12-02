#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _findRawContent
from telegram_util import matchKey

def _yieldPossibleAuthorItem(soup):
	yield soup.find("meta", {"name": "byl"})
	yield soup.find("span", {"class" : "byline__name"})
	yield soup.find("meta", {"property": "article:author"})
	yield soup.find("meta", {"name": "author"})
	yield soup.find("a", {"id" : "js_name"})
	for item in soup.find_all('meta'):
		if 'author' in str(item.attrs):
			yield item
		
def _yieldPossibleOrgItem(soup):
	yield soup.find("meta", {"property": "twitter:site"})
	yield soup.find("meta", {"property": "twitter:domain"})
	yield soup.find("meta", {"property": "og:site_name"})

def _findPossibleRawContent(item_iterator, words_to_ignore = []):
	for item in item_iterator:
		if not item:
			continue
		r = _findRawContent(item)
		if r and not matchKey(r, words_to_ignore):
			index = r.find(' - ')
			if index == -1:
				return r
			else:
				return r[:index]

def _findOrgName(soup):
	head = str(soup.find('head'))
	if matchKey(head, ['bbc.com']):
		return 'BBC', True
	if matchKey(head, ['nyt.com', 'new york times']):
		return 'NYT', True
	if matchKey(head, ['stackoverflow']):
		return 'StackOverflow', False
	if matchKey(head, ['medium.com']):
		return 'Medium', False
	if matchKey(head, ['dw.come']):
		return 'DW', True
	r = _findPossibleRawContent(_yieldPossibleOrgItem(soup))
	if r:
		return r, False
	return 'Source', False

def _findAuthor(soup):
	author_name = _findPossibleRawContent(
		_yieldPossibleAuthorItem(soup), 
		['://', 'http', 'www'])
	org, required = _findOrgName(soup)
	if not author_name:
		return org
	if not required or '-' in author_name:
		return author_name
	return author_name + ' - ' + org