#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _findRawContent
from telegram_util import matchKey

def getAttrString(attrs):
	if not attrs:
		return ''
	r = []
	for k, v in attrs.items():
		if k in ['content']:
			continue
		r.append(k + ': ' + str(v))
	return '\n'.join(r)

def _yieldPossibleAuthorItem(soup):
	yield soup.find("meta", {"name": "byl"})
	yield soup.find("span", {"class" : "byline__name"})
	for item in soup.find_all('meta'):
		if 'author' in getAttrString(item.attrs):
			yield item
	for item in soup.find_all('div', class_='news_about'):
		yield item.find('p')
	yield soup.find("a", {"id" : "js_name"})
	yield soup.find('a', class_='author-url')
	yield soup.find('span', class_='posted-date')
	yield soup.find('a', class_='name')
	yield soup.find('div', class_='article-author')
	yield soup.find("meta", {"name": "application-name"})
	for item in soup.find_all('a'):
		if matchKey(getAttrString(item.attrs), ['author']):
			yield item
	for item in soup.find_all('a'):
		if matchKey(getAttrString(item.attrs), ['/people/']):
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