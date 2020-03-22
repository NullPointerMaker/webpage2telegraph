#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'export_to_telegraph'
token = ''

from html_telegraph_poster import TelegraphPoster
from .article import _getArticle
from .common import _seemsValidText
from telegram_util import matchKey
from bs4 import BeautifulSoup

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

def getArticle(url, throw_exception=False, toSimplified=False):
	try:
		return _getArticle(_formaturl(url), toSimplified=toSimplified)
	except Exception as e:
		if throw_exception:
			raise e

def isConfidentUrl(url):
	return matchKey(url, ['mp.weixin.qq.com', 'stackoverflow', 'bbc', 'nyt', 'telegra'])

def isConfident(url, soup):
	if not isConfidentUrl(url):
		return False
	if not _seemsValidText(soup):
		return False
	for item in soup.find_all('figure'):
		img = item.find('img')
		if img and img.get('src', '').startswith('http'):
			return True
	return False

def _getTelegraphPath(url):
	marker = 'telegra.ph/'
	index = url.find(marker)	
	if index == -1:
		return
	return url[index + len(marker):]

def get(url):
	p = _getPoster()
	r = p._api_request('getPage', {
		'path': _getTelegraphPath(url),
		'fields': ['canEdit', 'can_edit'],
		'access_token': token
	})
	return r.get('result', {})

def _isEditable(p, url):
	path = _getTelegraphPath(url)
	if not path:
		return False
	r = p._api_request('getPage', {
		'path': path,
		'fields': ['can_edit'],
		'access_token': token
	})
	if not r:
		return False
	r = r.get('result', {})
	if r.get('can_edit'):
		return True
	# seems telegra.ph api stop to return the can_edit field, use confidenturl heuristics instead
	return isConfidentUrl(r.get('author_url')) 

def export(url, throw_exception=False, force=False, toSimplified=False):
	try:
		if not force and not isConfidentUrl(url):
			return
		p = _getPoster()
		if not force and _isEditable(p, url):
			return url
		article = getArticle(url, throw_exception, toSimplified=toSimplified)
		if not article.text or not article.text.text.strip():
			article.text = '<div>TO BE ADDED</div>'
		try:
			r = p.post(
				title = article.title, 
				author = article.author, 
				author_url = _formaturl(article.url or url), 
				text = str(article.text))
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

def clearUrl(url):
	if 'weibo' in url:
		index = url.find('?')
		if index > -1:
			url = url[:index]
	if url.endswith('/'):
		url = url[:-1]
	if '_' in url:
		url = '[网页链接](%s)' % url
	url = url.replace('https://', '')
	url = url.replace('http://', '')
	return url

def exportAllInText(soup):
	text = str(soup).replace('<br/>', '\n')
	quote = BeautifulSoup(text, features='lxml').text.strip()
	for link in soup.find_all('a', title=True, href=True):
		url = link['title']
		url = clearUrl(export_to_telegraph.export(url) or url)
		quote = quote.replace(link['href'], ' ' + url + ' ')
	quote = quote.replace('  ', ' ')
	quote = quote.replace('\n ', '\n')
	return quote