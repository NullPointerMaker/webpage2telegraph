#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'webpage2telegraph'
token = ''

from html_telegraph_poster import TelegraphPoster
from .article import _getArticle, getTitle, getAuthor
from .common import _seemsValidText
from telegram_util import matchKey
from bs4 import BeautifulSoup
from telegram_util import escapeMarkdown, clearUrl


def _get_poster():
	global token
	if token:
		return TelegraphPoster(access_token=token)
	p = TelegraphPoster()
	r = p.create_api_token('webpage2telegraph', 'webpage2telegraph')
	token = r['access_token']
	return p


def _trim_url(url):
	if not '://' in url:
		return url
	loc = url.find('://')
	return url[loc + 3:]


def _format_url(url):
	if '://' not in url:
		return "http://" + url
	return url


def get_article(url, throw_exception=False, simplify=False, force_cache=False):
	try:
		return _getArticle(_format_url(url), simplify=simplify, force_cache=force_cache)
	except Exception as e:
		if throw_exception:
			raise e


def is_confident_url(url):
	return matchKey(url, ['mp.weixin.qq.com', 'stackoverflow', 'bbc', 'nyt', 'telegra'])


def is_confident(url, soup):
	if not is_confident_url(url):
		return False
	if not _seemsValidText(soup):
		return False
	for item in soup.find_all('figure'):
		img = item.find('img')
		if img and img.get('src', '').startswith('http'):
			return True
	return False


def _get_telegraph_path(url):
	marker = 'telegra.ph/'
	index = url.find(marker)
	if index == -1:
		return
	return url[index + len(marker):]


def get(url):
	p = _get_poster()
	r = p._api_request('getPage', {
		'path': _get_telegraph_path(url),
		'fields': ['canEdit', 'can_edit'],
		'access_token': token
	})
	return r.get('result', {})

def get_author_url(article, url, source):
	if source:
		return ''
	return _format_url(article.url or url)


def get_author_field(author, source):
	if author == '原文' and not source:
		return ''
	return author


def transfer(url, throw_exception=False, force=False, simplify=False, force_cache=False, source=False):
	try:
		p = _get_poster()
		article = get_article(url, throw_exception, simplify=simplify, force_cache=force_cache)
		if not article.text or not article.text.text.strip():
			article.text = '<div>TO BE ADDED</div>'
		try:
			r = p.post(
				title=article.title,
				author=get_author_field(article.author, source),
				author_url=get_author_url(article, url, source),
				text=str(article.text))
		except Exception as e:
			if 'CONTENT_TEXT_REQUIRED' in str(e):
				r = p.post(
					title=article.title,
					author=get_author_field(article.author, source),
					author_url=get_author_url(article, url, source),
					text='<div>TO BE ADDED</div>')
			elif 'ACCESS_TOKEN_INVALID' in str(e):
				r = TelegraphPoster().post(
					title=article.title,
					author=get_author_field(article.author, source),
					author_url=get_author_url(article, url, source),
					text=str(article.text))
			else:
				raise e
		if force or is_confident(url, article.text):
			return _trim_url(r['url'])
	except Exception as e:
		if throw_exception:
			raise e


# TODO: may be remove this to another util? I don't want telegram util be
# depends on transfer to telegraph, that's why this util function is here...
def exportAllInText(soup):
	if not soup:
		return ''
	text = str(soup).replace('<br/>', '\n')
	quote = BeautifulSoup(text, features='lxml').text.strip()
	for link in soup.find_all('a', title=True, href=True):
		url = link['title']
		url = clearUrl(transfer(url) or url)
		if '_' in url:
			url = '[%s](%s)' % (url, url)
		quote = quote.replace(link['href'], ' ' + url + ' ')
	for link in soup.find_all('a', title=False, href=True):
		if link['href'] == link.text:
			quote.replace(link.text, ' ' + link.text + ' ')
	return escapeMarkdown(quote)
