#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common import _findRawContent
from bs4 import BeautifulSoup
from telegram_util import matchKey
import sys
from images import _cleanupImages
from tag_replace import _tagReplace
from final_touch import _finalTouch
from link import _replaceOfftopicLink
from offtopic import _decomposeOfftopic
from inner_article import _getInnerArticle

def saveSoup(soup, stage):
	if 'debug' in str(sys.argv):
		with open("tmp_%d.html" % stage, 'w') as f:
			f.write(str(soup))

def _findMainFromSoup(soup, url):
	saveSoup(soup, 0)
	soup = _replaceOfftopicLink(soup)
	saveSoup(soup, 1)
	soup = _decomposeOfftopic(soup, url)
	saveSoup(soup, 2)
	soup = _cleanupImages(soup, url)
	saveSoup(soup, 3)
	soup = _getInnerArticle(soup)
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