#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from readability import Document
from .title import _findTitle
from .author import _findAuthor
import hashlib
import readee
import sys

class _Article(object):
	def __init__(self, title, author, text, url = None):
		self.title = title
		self.author = author
		self.text = text
		self.url = url

def _findUrl(url, soup):
	if 'telegra.ph' not in url:
		return
	address = soup.find('address')
	if not address:
		return
	link = address.find('a')
	return link and link.get('href')

def _trimWebpage(raw):
	anchor = '<!-- detail_toolbox -->'
	index = raw.find(anchor)
	if index != -1:
		return raw[:index]
	return raw

def _getUrlContent(url):
	headers = {
		'method': 'GET',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
	}
	return requests.get(url, headers=headers).text

def _cachedContent(url):
	cache = 'tmp_' + hashlib.sha224(url.encode('utf-8')).hexdigest()[:10] + '.html'
	try:
		with open(cache) as f:
			return f.read()
	except:
		content = _getUrlContent(url)
		with open(cache, 'w') as f:
			f.write(content)
		return content

def _getArticle(url):
	if 'test' in str(sys.argv):
		content = _cachedContent(url)
	else:
		content = _getUrlContent(url)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	article_url = _findUrl(url, soup)
	doc = Document(content)
	return _Article(
		_findTitle(soup, doc), 
		_findAuthor(soup), 
		readee.export(url, content=content, list_replace=True, move_head_photo=True),
		article_url)