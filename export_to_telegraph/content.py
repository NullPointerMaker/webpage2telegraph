#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from .common import _findRawContent
from .domain import _findDomain
from .final_touch import _finalTouch, _moveHeadPhoto
from .images import _cleanupImages
from .inner_article import _getInnerArticle
from .link import _replaceOfftopicLink
from .offtopic import _decomposeOfftopic
from .tag_replace import _tagReplace
from telegram_util import matchKey
import sys

def saveSoup(soup, stage):
	if 'debug' in str(sys.argv):
		with open("tmp_%d.html" % stage, 'w') as f:
			f.write(str(soup))

def _findMainFromSoup(soup, url):
	domain = _findDomain(soup, url)
	saveSoup(soup, 0)
	soup = _replaceOfftopicLink(soup)
	saveSoup(soup, 1)
	soup = _decomposeOfftopic(soup, url)
	saveSoup(soup, 2)
	soup = _cleanupImages(soup, domain)
	saveSoup(soup, 3)
	soup, before_content = _getInnerArticle(soup)
	saveSoup(soup, 4)
	soup = _tagReplace(soup)
	saveSoup(soup, 5)
	soup = _finalTouch(soup, url)
	saveSoup(soup, 6)
	_moveHeadPhoto(soup, before_content)
	saveSoup(soup, 7)
	return soup

def _findMain(soup, doc, url):
	result = _findMainFromSoup(soup, url)
	if result:
		return result
	result = _findMainFromSoup(BeautifulSoup(doc.content), url)
	if result:
		return result
	return doc.content()