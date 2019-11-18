#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'export_to_telegraph'
token = ''

from html_telegraph_poster import TelegraphPoster
from .article import _getArticle
from .common import _seemsValidText

def _getPoster():
	global token
	if token:
		return TelegraphPoster(access_token = token)
	p = TelegraphPoster()
	r = p.create_api_token('export_to_telegraph', 'export_to_telegraph')
	token = r['access_token']
	return p

def _trimUrl(url):
	if not '://' in url:
		return url
	loc = url.find('://')
	return url[loc + 3:]

def _formaturl(url):
	if '://' not in url:
		return "https://" + url
	return url

def getArticle(url, throw_exception=False):
	try:
		return _getArticle(_formaturl(url))
	except Exception as e:
		if throw_exception:
			raise e

def isConfident(url, soup):
	if not matchKey(url, ['mp.weixin.qq.com', 'stackoverflow', 'bbc', 'nyt', 'telegra']):
		return False
	if not _seemsValidText(soup):
		return False
	for item in soup.find_all('figure'):
		img = item.find('img')
		if img and img.get('src', '').startswith('http'):
			return True
	return False

def export(url, throw_exception=False, force=False):
	try:
		p = _getPoster()
		article = getArticle(url, throw_exception)
		if not article.text or not article.text.text.strip():
			article.text = '<div>TO BE ADDED</div>'
		try:
			r = p.post(
				title = article.title, 
				author = article.author, 
				author_url = _formaturl(article.url or url), 
				text = str(article.text)[:80000])
		except Exception as e:
			if 'CONTENT_TEXT_REQUIRED' in str(e):
				r = p.post(
					title = article.title, 
					author = article.author, 
					author_url = _formaturl(article.url or url), 
					text = '<div>TO BE ADDED</div>')
			else:
				raise e
		if force or isConfident(url, article.text):
			return _trimUrl(r['url'])
	except Exception as e:
		if throw_exception:
			raise e
