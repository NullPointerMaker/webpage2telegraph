from common import _findRawContent
from bs4 import BeautifulSoup
from telegram_util import matchKey
import re

def fact():
	return BeautifulSoup("<div></div>", features="lxml")

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

def _formatImgUrl(raw, domain):
	parts = raw.split('/')
	success = False
	for index, part in enumerate(parts):
		if part == 'max':
			try:
				if int(parts[index + 1]) > 0:
					success = True
					break
			except:
				pass
	if success:
		parts[index + 1] = '1300'
	raw = '/'.join(parts)
	raw = re.sub('width=\d\d*', 'width=1300', raw)
	if raw.startswith('//'):
		return 'https:' + raw
	if raw.startswith('/'):
		return domain + raw
	return raw

MORE_CERTAIN_IMG_ATTRS = ['data-src-large', 'data-src']
IMG_ATTRS = MORE_CERTAIN_IMG_ATTRS + ['src'] # people would put junk in src field

def _getImgInsideFigure(figure, domain):
	for raw_img in figure.find_all():
		for attrs in IMG_ATTRS:
			if raw_img.get(attrs):
				r = fact().new_tag("img", src = _formatImgUrl(raw_img[attrs], domain))
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
	if not url:
		return 
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
				if r:
					return r
	for meta in soup.find_all('meta'):
		if 'url' in str(meta).lower():
			r = _parseDomain(_findRawContent(meta))
			if r:
				return r
	return _parseDomain(url)

def _getCaption(item):
	for x in item.find_all():
		if 'caption' in str(x).lower():
			caption = fact().new_tag("figcaption")
			caption.append(x)
			return caption

def _copyB(soup):
	return BeautifulSoup(str(soup), features="lxml")

def _findnoscriptImg(img):
	if not img.parent or len(str(img.parent)) > 1000:
		return
	if img.attrs and set(MORE_CERTAIN_IMG_ATTRS).intersection(set(img.attrs.keys())):
		return
	noscript = img.parent.find('noscript')
	if not noscript:
		return
	return noscript.find('img')

def _cleanupImages(soup, domain):
	for img in soup.find_all('img'):
		noscript_img = _findnoscriptImg(img)
		if noscript_img:
			img.replace_with(noscript_img)

	for figure in soup.find_all('figure'):
		r = _cleanupFigure(figure, domain)
		if r: 
			figure.replace_with(r)
	for img in soup.find_all('img'):
		if not img.parent:
			continue
		if img.parent.name == 'figure':
			continue
		caption = _getCaption(img.parent)
		figure = fact().new_tag("figure")
		figure.append(_copyB(img))
		if caption:
			figure.append(_copyB(caption))
			caption.decompose()
		r = _cleanupFigure(figure, domain)
		img.replace_with(_copyB(r))
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
	with open("tmp_%d.html" % stage, 'w') as f:
		f.write(str(soup))

def _findMainFromSoup(soup, url):
	domain = _findDomain(soup, url)
	saveSoup(soup, 0)
	soup = _cleanupImages(soup, domain)
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