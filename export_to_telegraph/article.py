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
from opencc import OpenCC
import cached_url
import time
import yaml
from telegram_util import matchKey, getWid
import weibo_2_album

cc = OpenCC('tw2sp')

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

def getContentFromAlbum(r):
	result = []
	for url in r.imgs:
		result.append('<img src="%s" />' % url)
	return '<div><title>%s</title>%s%s</div>' % \
		(r.title, r.cap_html, ''.join(result))

def getContent(url, force_cache=False):
	if 'weibo.c' in url:
		wid = getWid(url)
		if matchKey(url, ['card', 'ttarticle']):
			new_url = 'https://card.weibo.com/article/m/aj/detail?id=' + wid + '&_t=' + str(int(time.time()))
			json = yaml.load(cached_url.get(new_url, 
				headers={'referer': url}, force_cache = force_cache), Loader=yaml.FullLoader)
			return '<div><title>%s</title>%s</div>' % (json['data']['title'], json['data']['content'])
		return getContentFromAlbum(weibo_2_album.get(url))
	return cached_url.get(url, force_cache=force_cache)
	
def _getArticle(url, toSimplified=False, force_cache=False):
	content = getContent(url, force_cache=force_cache)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	article_url = _findUrl(url, soup)
	doc = Document(content)
	article = _Article(
		_findTitle(soup, doc), 
		_findAuthor(soup), 
		readee.export(url, content=content, list_replace=True, 
			toSimplified=toSimplified),
		article_url)
	if toSimplified:
		article.title = cc.convert(article.title)
		article.author = cc.convert(article.author)
	return article