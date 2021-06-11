#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _findRawContent

def _similarSingle(p, mediaName):
	return mediaName.lower() in p.lower() and (len(p) - len(mediaName)) < 10

def _similar(p, mediaNames):
	return any([_similarSingle(p, m) for m in mediaNames])

to_remove_ends = ['| 自由微信 | FreeWeChat', ' | 地球圖輯隊 帶你看透全世界']

def _cleanupRawTitle(raw):
	raw = ''.join(raw.split('BBC Learning English - '))
	for end in to_remove_ends:
		if raw.endswith(end):
			raw = raw[:-len(end)]
	mediaNames = ['nyt', 'new york times', 'stackoverflow', 'bbc', 'opinion']
	index = raw.rfind('- ')
	if index != -1:
		raw = raw[:index]
	raw = raw.strip()
	parts = raw.split('|')
	parts = [p for p in parts if not _similar(p, mediaNames)]
	return ('|'.join(parts)).strip()

def _yieldPossibleTitleItem(soup):
	yield soup.find("meta", {"property": "twitter:title"})
	yield soup.find("meta", {"name": "twitter:title"})
	yield soup.find("h1", class_='single-post-title')
	yield soup.find("h1", class_='news_title')
	yield soup.find("h1", class_='entry-title')
	yield soup.find('table', class_='infobox')
	yield soup.find("h1", class_='title')
	yield soup.find("h1", class_='story_art_title')
	yield soup.find("h1", class_='post-head')
	yield soup.find("h2", class_='question-title')
	yield soup.find("title")
	yield soup.find("h1")
	yield soup.find('meta', property='og:title')
	yield soup.find("h2")

	for item in soup.find_all('meta'):
		if 'title' in str(item.attrs):
			yield item

def _findTitleFromItem(item):
	raw = _findRawContent(item)
	return _cleanupRawTitle(raw) 

def _findTitle(soup, doc):
	for item in _yieldPossibleTitleItem(soup):
		if not item:
			continue
		result = _findTitleFromItem(item)
		if result and len(result) < 200:
			return result
	return _cleanupRawTitle(doc.title())