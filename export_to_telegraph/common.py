from bs4 import BeautifulSoup

def _findRawContent(item):
	if item.has_attr('content'):
		title = item['content'].strip()
		if title:
			return title
	return item.text.strip()

def fact():
	return BeautifulSoup("<div></div>", features="lxml")

def _copyB(soup):
	return BeautifulSoup(str(soup), features="lxml")