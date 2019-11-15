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
	yield soup.find("a", {"id" : "js_name"})
	yield soup.find("meta", {"property": "article:author"})
	yield soup.find("meta", {"name": "byl"})

def _yieldPossibleOrgItem(soup):
	yield soup.find("meta", {"property": "twitter:site"})
	yield soup.find("meta", {"property": "twitter:domain"})
	yield soup.find("meta", {"property": "og:site_name"})

def _findPossibleRawContent(item_iterator):
	for item in item_iterator:
		if not item:
			continue
		r = _findRawContent(item)
		if r:
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
	author_name = _findPossibleRawContent(_yieldPossibleAuthorItem(soup))
	org, required = _findOrgName(soup)
	if not author_name:
		return org
	if not required:
		return author_name
	return author_name + ' - ' + org

ADS_WORDS = [
	'The Times is committed', 
	'Follow The New York Times',
	'《纽约时报》推出每日中文简报',
	'订阅《纽约时报》中文简报',
]

def _getInnerArticle(soup):
	soup = soup.find("article") or soup
	soup = soup.find("div", {"id" : "js_content"}) or soup
	soup = soup.find("div", class_ = "story-body__inner") or soup
	soup = soup.find("div", class_ = "answercell") or soup
	soup = soup.find("div", class_ = "post-text") or soup
	return soup

def _decomposeOfftopic(soup):
	# TODO: head photo or opionion article missing?
	lists = [
		soup.find_all('span', class_="off-screen"),
		soup.find_all('ul', class_="story-body__unordered-list"),
		soup.find_all('span', class_="story-image-copyright"),
		soup.find_all("div", class_="article-header"),
		soup.find_all("small"),
		soup.find_all("header"),
		soup.find_all("div", {"id":"top-wrapper"}),
		soup.find_all("div", class_="bottom-of-article"),
		soup.find_all("div", {"id":"bottom-wrapper"}),
		soup.find_all('h1'),
		soup.find_all('address'),
	]
	for r in lists:
		for elm in r:	
			elm.decompose()
	return soup

def _replaceOfftopicLink(soup):
	for link in soup.find_all("a"):
		if not matchKey(link.text, ['英文版']):
			link.replace_with(link.text)
	return soup

def _tagReplace(soup):
	for img in soup.find_all("img"):
		b = soup.new_tag("figure")
		b.append(soup.new_tag("img", src = img["data-src"]))
		img.append(b)
	for img in soup.find_all("div", class_="js-delayed-image-load"):
		b = soup.new_tag("figure", width=img['data-width'], height=img['data-height'])
		b.append(soup.new_tag("img", src = img["data-src"], width=img['data-width'], height=img['data-height']))
		img.replace_with(b)
	for section in soup.find_all("section"):
		b = soup.new_tag("p")
		b.append(BeautifulSoup(str(section), features="lxml"))
		section.replace_with(b)
	for item in soup.find_all("div", class_="article-paragraph"):
		wrapper = soup.new_tag("p")
		wrapper.append(BeautifulSoup(str(item), features="lxml"))
		item.replace_with(wrapper)
	return soup

def _removeAds(soup):
	lists = [
		soup.find_all("p"),
		soup.find_all("div")
	]
	for l in lists:
		for item in l:
			if matchKey(item.text, ADS_WORDS) or item.text in ['广告']:
				item.decompose()
	for item in soup.find_all("footer", class_="author-info"):
		for subitem in item.find_all("a"):
			if subitem.text and "英文版" in subitem.text:
				item.replace_with(subitem)
				break
	return soup

def _findTextFromSoup(soup):
	soup = _getInnerArticle(soup)
	soup = _decomposeOfftopic(soup)
	soup = _replaceOfftopicLink(soup)
	soup = _tagReplace(soup)
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

def _getArticle(url):
	print(1, url)
	r = requests.get(url)
	print(2, url)
	soup = BeautifulSoup(r.text, 'html.parser')
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
	'https://www.nytimes.com/2019/10/10/opinion/sunday/feminism-lean-in.html',
	'https://www.nytimes.com/2019/11/14/opinion/teen-girls-jailed.html?smid=fb-nytimes&smtyp=cur&fbclid=IwAR20qM1vb1lD0NGUYQNDXnp657ImPUdRovc0H-dV--RQENiQu5f1OW4Ko6o',
	'bbc.in/2W2Gohc',
	'cn.nytimes.com/china/20191018/hong-kong-protests/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'cn.nytimes.com/technology/20191009/china-propaganda-patriotism/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'http://www.bbc.com/zhongwen/simp/world-49968707?ocid=socialflow_twitter',
	'https://cn.nytimes.com/asia-pacific/20191017/kim-jong-un-horse/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://cn.nytimes.com/china/20191012/china-hong-kong-education/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://cn.nytimes.com/china/20191018/hong-kong-protests/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://cn.nytimes.com/china/20191021/hong-kong-protesters-letters/',
	'https://cn.nytimes.com/opinion/20191018/chinese-nationalism/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://cn.nytimes.com/technology/20191009/china-propaganda-patriotism/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://cn.nytimes.com/world/20191015/mekong-river-dams-china/?utm_source=tw-nytimeschinese&utm_medium=social&utm_campaign=cur',
	'https://mp.weixin.qq.com/s/06MIEmocfuijPBvnSXAaUA',
	'https://mp.weixin.qq.com/s/21eVx37l7dUav6UZ4g60OA',
	'https://mp.weixin.qq.com/s/5Xt-A9y9fYg03aOueQLKaw',
	'https://mp.weixin.qq.com/s/_2Ryn4hsETbFHX9tOLXrYg',
	'https://mp.weixin.qq.com/s/cN13F-ZbnVTrfrfCWedFAg',
	'https://mp.weixin.qq.com/s/GXxHDu8ABf4JaFCvZemFSA',
	'https://mp.weixin.qq.com/s/LiP3CXIbDfvkbCTtmFXc-g',
	'https://mp.weixin.qq.com/s/pQ-fHOuFvQWa_UocabsaVw',
	'https://mp.weixin.qq.com/s/tRq5-zg1PZFtIrPAdG28Ow',
	'https://mp.weixin.qq.com/s/x1oQSf3BrFt-uas1uqw_BA',
	'https://mp.weixin.qq.com/s/XYB0hbJpR1E_JyZR7GQyCQ',
	'https://mp.weixin.qq.com/s?__biz=MzIxNjI2MTQzNw==&mid=2650597823&idx=1&sn=db173dd7bd27b12d95440d1fa65b3137&chksm=8f83ffedb8f476fbb2dde0e3c48b074d32ffbc0b49c79a5c9aef1551a6953ee2ca986d210b95&token=2015445412&lang=zh_CN#rd',
	'https://onezero.medium.com/how-morality-can-help-us-disconnect-68b2b695f7e6',
	'https://stackoverflow.com/questions/41299085/how-to-make-a-hyperlink-in-telegram-without-bot',
	'https://t.co/Joty1jyQwt',
	'https://t.co/k2kLBpdQhl',
	'https://telegra.ph/%E7%A4%BE%E4%BA%A4%E5%AA%92%E4%BD%93%E6%97%B6%E4%BB%A3%E4%B8%AD%E5%9B%BD%E6%94%BF%E5%BA%9C%E5%A6%82%E4%BD%95%E8%AE%A9%E5%B9%B4%E8%BD%BB%E4%BA%BA%E5%8F%98%E5%BE%97%E7%88%B1%E5%9B%BD-10-09-23',
	'https://telegra.ph/how-to-make-a-hyperlink-in-telegram-without-bot---Stack-Overflow-10-08',
	'https://telegra.ph/Tales-From-the-Teenage-Cancel-Culture-11-01',
	'https://telegra.ph/库克船长抵达新西兰250周年庆祝还是抗议-10-09-2',
	'https://www.bbc.com/ukchina/simp/vert-cap-46678325',
	'https://www.bbc.com/ukchina/simp/vert-cap-46678325?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/chinese-news-49972809?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/chinese-news-49997574?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/chinese-news-50125713',
	'https://www.bbc.com/zhongwen/simp/chinese-news-50371045?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/science-50313320?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/world-48822470',
	'https://www.bbc.com/zhongwen/simp/world-49968707',
	'https://www.bbc.com/zhongwen/simp/world-50034631?ocid=socialflow_twitter',
	'https://www.bbc.com/zhongwen/simp/world-50038147?ocid=socialflow_twitter',
	'https://www.dw.com/zh/%E5%9B%BD%E9%99%85%E8%AE%BA%E5%9D%9B-%E5%9B%BE%E5%AF%BB%E6%96%B0%E7%96%86%E9%97%AE%E9%A2%98%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95/a-50911411',
	'https://www.dw.com/zh/%E6%91%A9%E6%A0%B9%E5%A4%A7%E9%80%9A%E4%B8%80%E5%A4%A7%E9%99%86%E7%B1%8D%E5%91%98%E5%B7%A5%E5%9C%A8%E9%A6%99%E6%B8%AF%E9%81%AD%E6%9A%B4%E6%89%93/a-50723184',
	'https://www.nytimes.com/2019/02/27/us/immigrant-children-sexual-abuse.html?fbclid=IwAR16r7kJBO-V8rK9shUzMInmIbrZycQZFzh1Mujl5mFyNiF1oqkWW8zYqME',
	'https://www.nytimes.com/2019/10/10/opinion/sunday/feminism-lean-in.html',
	'https://www.nytimes.com/2019/11/14/opinion/teen-girls-jailed.html?smid=fb-nytimes&smtyp=cur&fbclid=IwAR20qM1vb1lD0NGUYQNDXnp657ImPUdRovc0H-dV--RQENiQu5f1OW4Ko6o',
	'telegra.ph/香港抗议僵局难解亲北京阵营陷入分歧-10-18',
	'www.bbc.com/zhongwen/simp/world-49968707?ocid=socialflow_twitter',
	'https://t.co/4ik2VsUHeB',
]

def _test():
	random.shuffle(urls)
	random.shuffle(urls)
	for url in urls[:1]:
		r = export(url, True)
		print('\t', r, url)


_test()
