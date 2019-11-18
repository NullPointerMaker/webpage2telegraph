#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey
from .images import _yieldPossibleImg

def _replaceOfftopicLink(soup):
	for link in soup.find_all("a"):
		if matchKey(link.text, ['英文版']):
			continue
		img = next(_yieldPossibleImg(link), None)
		if img:
			link.replace_with(img)
			continue
		if link.text and link.text.strip():
			link.replace_with(link.text)
			continue
		link.decompose()
	return soup