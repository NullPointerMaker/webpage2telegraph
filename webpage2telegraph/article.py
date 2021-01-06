#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import gphoto_2_album
import weibo_2_album
import cached_url
import readee
import yaml
from bs4 import BeautifulSoup
from opencc import OpenCC
from readability import Document
from telegram_util import matchKey, getWid

from .author import _find_author
from .title import _find_title

cc = OpenCC('tw2sp')


class _Article(object):
	def __init__(self, title, author, text, url=None):
		self.title = title
		self.author = author
		self.text = text
		self.url = url


def _find_url(url, soup):
	if 'telegra.ph' not in url:
		return
	address = soup.find('address')
	if not address:
		return
	link = address.find('a')
	return link and link.get('href')


def _trim_webpage(raw):
	anchor = '<!-- detail_toolbox -->'
	index = raw.find(anchor)
	if index != -1:
		return raw[:index]
	return raw


def _get_content_from_album(r, no_text=False):
	result = []
	for url in r.imgs:
		result.append('<img src="%s" />' % url)
	if no_text:
		return '<div><title>%s</title>%s</div>' % (r.title, ''.join(result))
	return '<div><title>%s</title>%s%s</div>' % (r.title, r.cap_html, ''.join(result))


def _get_content(url, force_cache=False):
	if 'weibo.c' in url:
		wid = getWid(url)
		if matchKey(url, ['card', 'ttarticle']):
			new_url = 'https://card.weibo.com/article/m/aj/detail?id=' + wid + '&_t=' + str(int(time.time()))
			json = yaml.load(cached_url.get(new_url, headers={'referer': url}, force_cache=force_cache), Loader=yaml.FullLoader)
			return '<div><title>%s</title>%s</div>' % (json['data']['title'], json['data']['content'])
		return _get_content_from_album(weibo_2_album.get(url))
	if 'photos.google.com/share' in url:
		return _get_content_from_album(gphoto_2_album.get(url), no_text=True)
	return cached_url.get(url, force_cache=force_cache)


def get(url, simplify=False, force_cache=False):
	content = _get_content(url, force_cache=force_cache)
	soup = BeautifulSoup(_trim_webpage(content), 'html.parser')
	article_url = _find_url(url, soup)
	doc = Document(content)
	article = _Article(
		_find_title(soup, doc),
		_find_author(soup),
		readee.export(url, content=content, list_replace=True, toSimplified=simplify),
		article_url)
	if simplify:
		article.title = cc.convert(article.title)
		article.author = cc.convert(article.author)
	return article
