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
from telegram_util import matchKey, getWid, isCN, AlbumResult, cutCaptionHtml
import weibo_2_album
import gphoto_2_album
import hanzidentifier
from PIL import Image
import os

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

def getContentFromAlbum(r, noText=False):
	result = []
	for url in r.imgs:
		result.append('<img src="%s" />' % url)
	if noText: 
		return '<div><title>%s</title>%s</div>' % (r.title, ''.join(result))
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
	if 'photos.google.com/share' in url:
		return getContentFromAlbum(gphoto_2_album.get(url), noText=True)
	return cached_url.get(url, force_cache=force_cache)

def getTitle(url, force_cache=True, toSimplified = False, noAutoConvert=False):
	try:
		content = getContent(url, force_cache=force_cache)
		soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
		doc = Document(content)
		title =  _findTitle(soup, doc)
		to_simplify_calculated = calculateToSimplified(toSimplified, noAutoConvert, title)
		if to_simplify_calculated:
			return cc.convert(title)
		return title
	except:
		return 'No Title'

def getAuthor(url, force_cache=True):
	content = getContent(url, force_cache=force_cache)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	return _findAuthor(soup)

def calculateToSimplified(toSimplified, noAutoConvert, title):
	if toSimplified:
		return True
	if noAutoConvert:
		return False
	for c in title:
		if isCN(c) and not hanzidentifier.is_simplified(c):
			return True
	return False
	
def _getArticle(url, toSimplified=False, force_cache=False, noAutoConvert=False):
	content = getContent(url, force_cache=force_cache)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	article_url = _findUrl(url, soup)
	doc = Document(content)
	title = _findTitle(soup, doc)
	to_simplify_calculated = calculateToSimplified(toSimplified, noAutoConvert, title)
	article = _Article(
		title, 
		_findAuthor(soup), 
		readee.export(url, content=content, list_replace=True, 
			toSimplified=to_simplify_calculated),
		article_url)
	if to_simplify_calculated:
		article.title = cc.convert(article.title)
		article.author = cc.convert(article.author)
	return article

def isGoodLine(line):
	start_tags = ['作者 | ', '靠谱的新媒体不多', '图/', '图：', 
		'最近很多读者反映收不到', '【今日']
	for start_tag in start_tags:
		if line.startswith(start_tag):
			return False
	return True

def getAlbum(url, force_cache=True, word_limit=200, paragraph_limit=3, append_source=False, append_url = True):
	content = _getArticle(url, force_cache=force_cache).text
	album = AlbumResult()
	for item in content.findAll('img'):
		path = item.get('src')
		if not path:
			continue
		try:
			cached_url.get(path, mode='b', force_cache=True)
			img = Image.open(cached_url.getFilePath(path)) 
		except:
			continue
		w, h = img.size
		file_size = os.stat(cached_url.getFilePath(path)).st_size
		if 36000 < file_size < 36200 and w == 1080 and h == 1080: # 界面文化题头
			continue
		if 27000 < file_size < 27300 and w == 640 and h == 640: # 思想市场
			continue
		if w == 750 and h == 234: # 界面文化题头
			continue
		if 6000 < file_size < 9000 and w == 347 and h == 347: # 界面文化题头
			continue
		if 87000 < file_size < 91000 and w == 900 and h == 500: # 美国华人杂谈题头
			continue
		if w * 0.25 < h < w * 4 and min(w, h) > 100 and max(w, h) > 300:
			# print(file_size, w, h)
			album.imgs.append(item.get('src'))
			break
	for tag in ['img', 'br']:
		for item in content.findAll(tag):
			item.replace_with('\n\n')
	for item in content.findAll('p'):
		item.append('\n\n')
	title = '【%s】\n\n' % getTitle(url)
	lines = content.text.split('\n')
	lines = [line.strip() for line in lines]
	lines = [line for line in lines if isGoodLine(line)]
	if paragraph_limit < 5:
		lines = [line for line in lines if not line or len(line) > 20]
	lines = cutCaptionHtml('\n'.join(lines), word_limit).strip().strip('\ufeff').strip()
	lines = lines.split('\n')
	lines = lines[:paragraph_limit * 2]
	album.cap_html_v2 = title + '\n'.join(lines).strip()
	if append_url: 
		album.cap_html_v2 += '\n\n' + url
	if append_source:
		album.url = url
	return album