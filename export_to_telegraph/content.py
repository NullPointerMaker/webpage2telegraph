from common import _findRawContent
from bs4 import BeautifulSoup
from telegram_util import matchKey
import sys
from images import _cleanupImages
from common import *

OFFTOPIC_TAG = ['small', 'address', 'meta', 'script', 'noscript']

OFFTOPIC_ATT = [
	'social', 'comment', 'latest', 'widget', 'more', 'button', 'facebook', 
	'cn-carousel-medium-strip', 'video__end-slate__top-wrapper', 'metadata', 
	'el__article--embed', 'signup', 'related', 'disclaimer', 'off-screen', 
	'story-body__unordered-list', 'story-image-copyright', 'article-header', 
	'top-wrapper', 'bottom-of-article', 'bottom-wrapper', 'linkList', 
	'display:none;', 'accordion', 'el-editorial-source', 'video__end-slate__tertiary-title',
	'adblocker', 'tagline', 'navbar', 'navmenu', 'topHeader'
]

OFFTOPIC_CLASSES = ['ads']

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
	if 'sidebar' in attrs and not matchKey(attrs, ['no-sidebar']):
		return True
	if 'hidden' in attrs and not matchKey(attrs, ['lazy', 'false', 'label-hidden']):
		return True
	if 'copyright' in attrs and not 'and' in attrs:
		return True
	return False

def _decomposeOfftopic(soup, url):
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

	if not matchKey(url, ['medium']):
		for item in soup.find_all('h1'):
			item.decompose()

	for item in soup.find_all('figure'):
		if len(list(item.children)) == 0:
			item.decompose()
	return soup

def _replaceOfftopicLink(soup):
	for link in soup.find_all("a"):
		if matchKey(link.text, ['英文版']):
			continue
		if link.find('figure'):
			link.replace_with(link.find('figure'))
			continue
		if link.text and link.text.strip():
			link.replace_with(link.text)
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

def _finalTouch(soup, url):
	for item in soup.find_all("footer", class_="author-info"):
		for subitem in item.find_all("a"):
			if subitem.text and "英文版" in subitem.text:
				item.replace_with(subitem)
				break
	if 'pride.com' in url:
		for item in soup.find_all('h2'):
			item.parent.parent.insert(0, _copyB(item))
			item.decompose()
	for item in soup.find_all():
		if item.text == 'Follow  and !':
			item.decompose()
	return soup

def saveSoup(soup, stage):
	if len(sys.argv) > 1 and sys.argv[1].startswith('debug'):
		with open("tmp_%d.html" % stage, 'w') as f:
			f.write(str(soup))

def _findMainFromSoup(soup, url):
	saveSoup(soup, 0)
	soup = _cleanupImages(soup, url)
	saveSoup(soup, 1)
	soup = _decomposeOfftopic(soup, url)
	saveSoup(soup, 2)
	soup = _getInnerArticle(soup)
	saveSoup(soup, 3)
	soup = _replaceOfftopicLink(soup)
	saveSoup(soup, 4)
	soup = _tagReplace(soup)
	saveSoup(soup, 5)
	soup = _finalTouch(soup, url)
	saveSoup(soup, 6)
	return soup

def _findMain(soup, doc, url):
	result = _findMainFromSoup(soup, url)
	if result:
		return result
	result = _findMainFromSoup(BeautifulSoup(doc.content), url)
	if result:
		return result
	return doc.content()