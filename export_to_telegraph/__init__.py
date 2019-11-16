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

def fact():
	return BeautifulSoup("<div></div>", features="lxml")

OFFTOPIC_TAG = ['small', 'h1', 'address', 'meta', 'script', 'noscript']

OFFTOPIC_ATT = [
	'social', 'comment', 'latest', 'widget', 'more', 'button', 'facebook', 
	'cn-carousel-medium-strip', 'video__end-slate__top-wrapper', 'metadata', 
	'el__article--embed', 'sidebar', 'signup', 'related', 'disclaimer', 'off-screen', 
	'story-body__unordered-list', 'story-image-copyright', 'article-header', 
	'top-wrapper', 'bottom-of-article', 'bottom-wrapper', 'copyright', 'linkList', 
	'display:none;', 'accordion', 'el-editorial-source', 'video__end-slate__tertiary-title' 
]

OFFTOPIC_CLASSES = ['ads']

class _Article(object):
	def __init__(self, title, author, text, url = None):
		self.title = title
		self.author = author
		self.text = text
		self.url = url

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
	yield soup.find("meta", {"name": "author"})
	for item in soup.find_all('meta'):
		if 'author' in str(item.attrs):
			yield item
		
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
	if matchKey(head, ['bbc.com']):
		return 'BBC', True
	if matchKey(head, ['nyt.com', 'new york times']):
		return 'NYT', True
	if matchKey(head, ['stackoverflow']):
		return 'StackOverflow', False
	if matchKey(head, ['medium.com']):
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
	if not required or '-' in author_name:
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

def _seemsValidText(soup):
	if not soup:
		return False
	return soup.text and len(soup.text) > 500

def _seemsValidRawArticle(soup):
	if not _seemsValidText(soup):
		return False
	return not not soup.find('img')

def _getInnerArticle(soup):	
	applicators = [
		lambda x: x.find("article"),
		lambda x: x.find("div", {"id" : "js_content"}),
		lambda x: x.find("div", class_ = "story-body__inner"),
		lambda x: x.find("div", class_ = "answercell"),
		lambda x: x.find("div", class_ = "post-text"),
		lambda x: x.find("div", {"id" : "bodyContent"}),
		lambda x: x.find("div", {"id" : "content_JS"}),
	]
	for applicator in applicators:
		candidate = applicator(soup)
		if _seemsValidRawArticle(candidate):
			soup = candidate
	return soup

def _isOffTopic(attrs):
	if matchKey(attrs, OFFTOPIC_ATT):
		return True
	if 'hidden' in attrs and not 'lazy' in attrs:
		return True
	return False

def _decomposeOfftopic(soup):
	for item in soup.find_all():
		if _isOffTopic(str(item.attrs)) or \
			item.name in OFFTOPIC_TAG:
			item.decompose()

	for c in OFFTOPIC_CLASSES:
		for item in soup.find_all(class_=c):
			item.decompose()

	for item in soup.find_all("header"):
		wrapper = fact().new_tag("p")
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

def _getFullUrl(raw, domain):
	if raw.startswith('//'):
		return 'https:' + raw
	if raw.startswith('/'):
		return domain + raw
	return raw

IMG_ATTRS = ['data-src-large', 'data-src', 'src']

def _getImgInsideFigure(figure, domain):
	for raw_img in figure.find_all():
		for attrs in IMG_ATTRS:
			if raw_img.get(attrs):
				r = fact().new_tag("img", src = _getFullUrl(raw_img[attrs], domain))
				if raw_img.get('title'):
					r['title'] = raw_img.get('title')
				return r

def _cleanupFigure(figure, domain):
	img = _getImgInsideFigure(figure, domain)
	if not img:
		return
	caption = figure.find('figcaption')
	if not caption and img.get('title'):
		caption = fact().new_tag("figcaption")
		caption.append(img['title'])
	new_figure = fact().new_tag("figure")
	new_figure.append(img)
	if caption:
		new_figure.append(caption)
	for cite in new_figure.find_all('cite'):
		cite.decompose()
	return new_figure

def _parseDomain(url):
	if not url.startswith('http'):
		return
	r = '/'.join(url.split('/')[:3])
	if r.count('/') == 2 and 'http' in r:
		return r

def _findDomain(soup, url):
	for meta in soup.find_all('meta'):
		for att in meta.attrs:
			if 'url' in att.lower():
				r = _parseDomain(meta[att])
	return _parseDomain(url)

def _getCaption(item):
	for x in item.find_all():
		if 'caption' in str(x).lower():
			caption = fact().new_tag("figcaption")
			caption.append(x)
			return caption

def _cleanupImages(soup, url):
	domain = _findDomain(soup, url)
	for figure in soup.find_all('figure'):
		r = _cleanupFigure(figure, domain)
		if r: 
			figure.replace_with(r)
	for img in soup.find_all('img'):
		if img.parent.name != 'figure':
			to_replace = img
			caption = _getCaption(img.parent)
			figure = fact().new_tag("figure")
			figure.append(BeautifulSoup(str(img), features="lxml"))
			if caption:
				to_replace = img.parent
				figure.append(caption)

			r = _cleanupFigure(figure, domain)
			if r:
				to_replace.replace_with(r)
	return soup
		

def _tagReplace(soup):
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			item.decompose()
			continue
		wrapper = fact().new_tag("p")
		wrapper.append(BeautifulSoup(str(item), features="lxml"))
		item.replace_with(wrapper)
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			item.decompose()
	for section in soup.find_all("section"):
		b = fact().new_tag("p")
		b.append(BeautifulSoup(str(section), features="lxml"))
		section.replace_with(b)
	to_remove_tags = [
		soup.find_all("li"),
		soup.find_all("ul")
	]
	for l in to_remove_tags:
		for item in l:
			new_item = fact().new_tag("p")
			for x in item.find_all(recursive=False):
				new_item.append(x)
			item.replace_with(new_item)
	return soup

def _removeAds(soup):
	for item in soup.find_all("footer", class_="author-info"):
		for subitem in item.find_all("a"):
			if subitem.text and "英文版" in subitem.text:
				item.replace_with(subitem)
				break
	return soup

def _findTextFromSoup(soup, url):
	with open('tmp_0.html', 'w') as f:
		f.write(str(soup))
	soup = _getInnerArticle(soup)
	with open('tmp_a.html', 'w') as f:
		f.write(str(soup))
	soup = _cleanupImages(soup, url)
	with open('tmp_a1.html', 'w') as f:
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

def _findText(soup, doc, url):
	result = _findTextFromSoup(soup, url)
	if result:
		return result
	result = _findTextFromSoup(BeautifulSoup(doc.content), url)
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
	print('DEBUG WARNING, SHOULD NOT BE HERE')
	return _cleanupRawTitle(doc.title())

def _trimWebpage(raw):
	anchor = '<!-- detail_toolbox -->'
	index = raw.find(anchor)
	if index != -1:
		return raw[:index]
	return raw

def _findUrl(soup):
	address = soup.find('address')
	if not address:
		return
	link = address.find('a')
	return link and link.get('href')

def _getArticle(url):
	r = requests.get(url)
	soup = BeautifulSoup(_trimWebpage(r.text), 'html.parser')
	doc = Document(r.text)
	return _Article(
		_findTitle(soup, doc), 
		_findAuthor(soup), 
		_findText(soup, doc, url), 
		_findUrl(soup))

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
		r = p.post(
			title = article.title, 
			author = article.author, 
			author_url = _formaturl(article.url or url), 
			text = str(article.text)[:80000])
		if force or isConfident(url, article.text):
			return _trimUrl(r['url'])
	except Exception as e:
		if throw_exception:
			raise e

urls = [
	# 'https://www.telegraph.co.uk/global-health/women-and-girls/dumped-babies-just-tip-iceberg-deadly-consequences-curbing-reproductive/?fbclid=IwAR0uwFvu3QjbhnYyMxfeN2PtlczcgoiWASrEdRsikQ1Y5TTAO6_PpGH2nDk',
	# 'https://cn.nytimes.com/china/20191112/hong-kong-protests-volunteer/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	# 'https://telegra.ph/%E9%A6%99%E6%B8%AF%E6%8A%97%E8%AE%AE%E8%80%85%E8%83%8C%E5%90%8E%E7%9A%84%E5%BF%97%E6%84%BF%E8%80%85%E5%A4%A7%E5%86%9B-11-16',
	# 'https://www.pinknews.co.uk/2019/11/14/same-sex-marriage-in-sweden-and-denmark-has-reduced-the-number-of-lesbians-and-gay-men-dying-by-suicide-by-almost-half/?fbclid=IwAR2Rq8aPs7lACGJOmC_N549Px9QvZAYGeCjd8_Z-i5owBlLKbtX7UyGm4l8',
	# 'https://www.idiva.com/news-opinion/womens-issues/transgender-cabbies-who-are-making-indian-roads-safer-for-women/18004255?fbclid=IwAR3aOtNX0fOukmJ-JNJiImobMfPyVhQ63-i5oEUX38_TRlU4-aBLvHwmaA0',
	# 'https://www.eurekalert.org/pub_releases/2019-11/lu-ada111519.php',
	# 'https://www.nytimes.com/2019/10/10/opinion/sunday/feminism-lean-in.html',
	# 'bbc.in/2W2Gohc',
	# 'https://t.co/Joty1jyQwt',
	# 'https://t.co/k2kLBpdQhl',
	# 'https://t.co/4ik2VsUHeB',
	# 'https://www.dw.com/zh/%E6%91%A9%E6%A0%B9%E5%A4%A7%E9%80%9A%E4%B8%80%E5%A4%A7%E9%99%86%E7%B1%8D%E5%91%98%E5%B7%A5%E5%9C%A8%E9%A6%99%E6%B8%AF%E9%81%AD%E6%9A%B4%E6%89%93/a-50723184',
	# 'https://edition.cnn.com/2019/11/11/asia/mouse-deer-vietnam-chevrotain-rediscovered-scn/index.html',
]

def _test():
	for url in urls:
		print('原文：', url)
		r = export(url, True, True)
		print('导出：', r)
		print('\n\n')

_test()
