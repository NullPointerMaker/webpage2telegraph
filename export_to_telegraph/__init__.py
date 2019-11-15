#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'export_to_telegraph'
token = ''

import requests
from bs4 import BeautifulSoup
from html_telegraph_poster import TelegraphPoster
import traceback as tb
from readability import Document
import random
from telegram_util import matchKey

factory = BeautifulSoup("<div></div>", features="lxml")

class _Article(object):
	def __init__(self, title, author, text):
		self.title = title
		self.author = author
		self.text = text

def _getPoster():
	global token
	if token:
		return TelegraphPoster(access_token = token)
	p = TelegraphPoster()
	r = p.create_api_token('export_to_telegraph', 'export_to_telegraph')
	token = r['access_token']
	return p

def _yieldPossibleAuthorItem(soup):
	yield soup.find("meta", {"name": "byl"})
	yield soup.find("a", {"id" : "js_name"})
	yield soup.find("span", {"class" : "byline__name"})
	yield soup.find("meta", {"property": "article:author"})

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
			return r

def _findOrgName(soup):
	head = str(soup.find('head'))
	if matchKey(head, ['bbc']):
		return 'BBC', True
	if matchKey(head, ['nyt', 'new york times']):
		return 'NYT', True
	if matchKey(head, ['stackoverflow']):
		return 'StackOverflow', False
	if matchKey(head, ['medium']):
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
	if not required:
		return author_name
	return author_name + ' - ' + org

DIV_AD_WORDS = [
	'《纽约时报》推出每日中文简报',
	'订阅《纽约时报》中文简报',
]

P_AD_WORDS = [
	'The Times is committed', 
	'Follow The New York Times',
]

def _getInnerArticle(soup):
	soup = soup.find("article") or soup
	soup = soup.find("div", {"id" : "js_content"}) or soup
	soup = soup.find("div", class_ = "story-body__inner") or soup
	soup = soup.find("div", class_ = "answercell") or soup
	soup = soup.find("div", class_ = "post-text") or soup
	soup = soup.find("div", {"id" : "bodyContent"}) or soup
	return soup

def _decomposeOfftopic(soup):
	lists = [
		soup.find_all('span', class_="off-screen"),
		soup.find_all('ul', class_="story-body__unordered-list"),
		soup.find_all('span', class_="story-image-copyright"),
		soup.find_all("div", class_="article-header"),
		soup.find_all("small"),
		soup.find_all("div", {"id":"top-wrapper"}),
		soup.find_all("div", class_="bottom-of-article"),
		soup.find_all("div", {"id":"bottom-wrapper"}),
		soup.find_all('h1'),
		soup.find_all('address'),
		soup.find_all('span', {"itemprop": "copyrightHolder"}),
		soup.find_all('div', class_="linkList"),
		soup.find_all('div', {"style": "display:none;"}),
		soup.find_all('div', class_="accordion"),
	]
	for r in lists:
		for elm in r:	
			elm.decompose()

	for item in soup.find_all('div'):
		if 'social' in str(item['class']):
			item.decompose()

	for item in soup.find_all("header"):
		wrapper = factory.new_tag("p")
		s = item.find("p", {"id": "article-summary"})
		if s:
			wrapper.append(s)
		p = item.find("div", {"data-testid": "photoviewer-wrapper"})
		if p:
			wrapper.append(p)
		item.replace_with(wrapper)
	return soup

def _replaceOfftopicLink(soup):
	for link in soup.find_all("a"):
		if not matchKey(link.text, ['英文版']):
			if link.text and link.text.strip():
				link.replace_with(link.text)
			elif link.find('img'):
				link.replace_with(link.find('img'))
	return soup

def _tagReplace(soup):
	for img in soup.find_all("img"):
		if img.has_attr('data-src'):
			b = factory.new_tag("figure")
			b.append(factory.new_tag("img", src = img['data-src']))
			img.append(b)
			continue
		if img.has_attr('src') and img['src'].startswith('/image'):
			b = factory.new_tag("figure")
			b.append(factory.new_tag("img", src = 'https://www.dw.com' + img['src']))
			c = factory.new_tag("figcaption")
			if img.has_attr('title'):
				c.append(img['title'])
			b.append(c)
			img.replace_with(b)
	for img in soup.find_all("div", class_="js-delayed-image-load"):
		b = factory.new_tag("figure", width=img['data-width'], height=img['data-height'])
		b.append(factory.new_tag("img", src = img['data-src'], width=img['data-width'], height=img['data-height']))
		img.replace_with(b)
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			item.decompose()
			continue
		wrapper = factory.new_tag("p")
		wrapper.append(BeautifulSoup(str(item), features="lxml"))
		item.replace_with(wrapper)
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			item.decompose()
	for section in soup.find_all("section"):
		b = factory.new_tag("p")
		b.append(BeautifulSoup(str(section), features="lxml"))
		section.replace_with(b)
	return soup

def _removeAds(soup):
	lists = [
		soup.find_all("p"),
	]
	for item in soup.find_all("footer", class_="author-info"):
		for subitem in item.find_all("a"):
			if subitem.text and "英文版" in subitem.text:
				item.replace_with(subitem)
				break
	return soup

def _findTextFromSoup(soup):
	soup = _getInnerArticle(soup)
	with open('tmp_a.html', 'w') as f:
		f.write(str(soup))
	soup = _decomposeOfftopic(soup)
	with open('tmp_b.html', 'w') as f:
		f.write(str(soup))
	soup = _replaceOfftopicLink(soup)
	with open('tmp_c.html', 'w') as f:
		f.write(str(soup))
	soup = _tagReplace(soup)
	with open('tmp_d.html', 'w') as f:
		f.write(str(soup))
	soup = _removeAds(soup)
	return soup

def _findText(soup, doc):
	result = _findTextFromSoup(soup)
	if result:
		return result
	result = _findTextFromSoup(BeautifulSoup(doc.content))
	if result:
		return result
	return doc.content()


def _findRawContent(item):
	if item.has_attr('content'):
		title = item['content'].strip()
		if title:
			return title
	return item.text.strip()

def _similarSingle(p, mediaName):
	return mediaName.lower() in p.lower() and (len(p) - len(mediaName)) < 10

def _similar(p, mediaNames):
	return any([_similarSingle(p, m) for m in mediaNames])

def _cleanupRawTitle(raw):
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
	yield soup.find("title")
	yield soup.find("h1")
	yield soup.find("h2")

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
	print('DEBUG WARNING, SHOULD NOT BE HERE')
	return _cleanupRawTitle(doc.title())


def _trimWebpage(raw):
	anchor = '<!-- detail_toolbox -->'
	index = raw.find(anchor)
	if index != -1:
		return raw[:index]
	return raw

def _getArticle(url):
	r = requests.get(url)
	soup = BeautifulSoup(_trimWebpage(r.text), 'html.parser')
	doc = Document(r.text)
	return _Article(_findTitle(soup, doc), _findAuthor(soup), _findText(soup, doc))

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

def export(url, throw_exception=False):
	try:
		p = _getPoster()
		article = getArticle(url, throw_exception)
		r = p.post(
			title = article.title, 
			author = article.author, 
			author_url = _formaturl(url), 
			text = str(article.text)[:80000])
		return _trimUrl(r['url'])
	except Exception as e:
		if throw_exception:
			raise e

urls = [
	# 'https://www.nytimes.com/2019/10/10/opinion/sunday/feminism-lean-in.html',
	# 'bbc.in/2W2Gohc',
	# 'https://t.co/Joty1jyQwt',
	# 'https://t.co/k2kLBpdQhl',
	# 'https://t.co/4ik2VsUHeB',
	# 'https://www.dw.com/zh/%E6%91%A9%E6%A0%B9%E5%A4%A7%E9%80%9A%E4%B8%80%E5%A4%A7%E9%99%86%E7%B1%8D%E5%91%98%E5%B7%A5%E5%9C%A8%E9%A6%99%E6%B8%AF%E9%81%AD%E6%9A%B4%E6%89%93/a-50723184',
]

def _test():
	for url in urls[:1]:
		r = export(url, True)
		print('\t', r, url)

_test()
