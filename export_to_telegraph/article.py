import requests
from bs4 import BeautifulSoup
from readability import Document
from title import _findTitle
from author import _findAuthor
from content import _findMain

class _Article(object):
	def __init__(self, title, author, text, url = None):
		self.title = title
		self.author = author
		self.text = text
		self.url = url

def _findUrl(soup):
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

def _getArticle(url):
	r = requests.get(url)
	soup = BeautifulSoup(_trimWebpage(r.text), 'html.parser')
	article_url = _findUrl(soup)
	doc = Document(r.text)
	return _Article(
		_findTitle(soup, doc), 
		_findAuthor(soup), 
		_findMain(soup, doc, url), 
		article_url)