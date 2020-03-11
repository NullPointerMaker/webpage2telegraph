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
from hanziconv import HanziConv

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

def _getArticle(url, toSimplified=False):
	content = cached_url.get(url)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	article_url = _findUrl(url, soup)
	doc = Document(content)
	article = _Article(
		_findTitle(soup, doc), 
		_findAuthor(soup), 
		readee.export(url, content=content, list_replace=True, move_head_photo=True, 
			toSimplified=toSimplified),
		article_url)
	if toSimplified:
		article.title = HanziConv.toSimplified(article.title)
		article.author = HanziConv.toSimplified(article.author)
	return article